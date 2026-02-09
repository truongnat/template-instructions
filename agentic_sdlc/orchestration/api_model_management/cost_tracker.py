"""
Cost tracking and reporting for API Model Management.

This module provides cost tracking functionality including recording costs per request,
aggregating costs by various dimensions, checking budget thresholds, and persisting
cost data to SQLite for historical analysis.
"""

import aiosqlite
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from .models import BudgetStatus
from .exceptions import BudgetExceededError


logger = logging.getLogger(__name__)


class CostTracker:
    """
    Tracks and reports API usage costs.
    
    Responsibilities:
    - Record costs per request with model, agent type, and task details
    - Aggregate costs by model, provider, agent type, and time period
    - Check budget thresholds and trigger alerts
    - Persist cost data to SQLite for historical analysis
    - Provide cost query interface for reporting
    """
    
    def __init__(
        self,
        db_path: Path,
        daily_budget: float = 100.0
    ):
        """
        Initialize cost tracker.
        
        Args:
            db_path: Path to SQLite database file
            daily_budget: Daily budget limit in dollars (default: $100)
        """
        self.db_path = db_path
        self.daily_budget = daily_budget
        logger.info(f"Initialized CostTracker with daily budget: ${daily_budget:.2f}")
    
    async def record_cost(
        self,
        model_id: str,
        agent_type: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        task_id: str
    ) -> None:
        """
        Record cost for a completed request.
        
        Args:
            model_id: ID of the model used
            agent_type: Type of agent making the request
            input_tokens: Number of input tokens consumed
            output_tokens: Number of output tokens generated
            cost: Total cost in dollars
            task_id: ID of the task
        """
        timestamp = datetime.now()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO cost_records 
                (timestamp, model_id, agent_type, task_id, input_tokens, output_tokens, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (timestamp, model_id, agent_type, task_id, input_tokens, output_tokens, cost)
            )
            await db.commit()
        
        logger.debug(
            f"Recorded cost: ${cost:.4f} for model={model_id}, "
            f"agent={agent_type}, task={task_id}, "
            f"tokens={input_tokens}+{output_tokens}"
        )
    
    async def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """
        Get total cost for a specific day.
        
        Args:
            date: Date to query (default: today)
            
        Returns:
            Total cost in dollars for the specified day
        """
        if date is None:
            date = datetime.now()
        
        # Get start and end of day
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = start_of_day + timedelta(days=1)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT COALESCE(SUM(cost), 0.0) as total_cost
                FROM cost_records
                WHERE timestamp >= ? AND timestamp < ?
                """,
                (start_of_day, end_of_day)
            )
            row = await cursor.fetchone()
            total_cost = row[0] if row else 0.0
        
        logger.debug(f"Daily cost for {date.date()}: ${total_cost:.2f}")
        return total_cost

    async def get_cost_by_model(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Get costs aggregated by model for a time period.
        
        Args:
            start_date: Start of time period (inclusive)
            end_date: End of time period (exclusive)
            
        Returns:
            Dictionary mapping model_id to total cost
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT model_id, SUM(cost) as total_cost
                FROM cost_records
                WHERE timestamp >= ? AND timestamp < ?
                GROUP BY model_id
                ORDER BY total_cost DESC
                """,
                (start_date, end_date)
            )
            rows = await cursor.fetchall()
            
            result = {row[0]: row[1] for row in rows}
        
        logger.debug(
            f"Cost by model from {start_date.date()} to {end_date.date()}: "
            f"{len(result)} models"
        )
        return result
    
    async def get_cost_by_provider(
        self,
        start_date: datetime,
        end_date: datetime,
        model_registry: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """
        Get costs aggregated by provider for a time period.
        
        Args:
            start_date: Start of time period (inclusive)
            end_date: End of time period (exclusive)
            model_registry: Optional mapping of model_id to provider
            
        Returns:
            Dictionary mapping provider to total cost
        """
        cost_by_model = await self.get_cost_by_model(start_date, end_date)
        
        if model_registry is None:
            # If no registry provided, return costs by model_id
            return cost_by_model
        
        # Aggregate by provider
        cost_by_provider: Dict[str, float] = {}
        for model_id, cost in cost_by_model.items():
            provider = model_registry.get(model_id, "unknown")
            cost_by_provider[provider] = cost_by_provider.get(provider, 0.0) + cost
        
        logger.debug(
            f"Cost by provider from {start_date.date()} to {end_date.date()}: "
            f"{len(cost_by_provider)} providers"
        )
        return cost_by_provider
    
    async def get_cost_by_agent_type(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Get costs aggregated by agent type for a time period.
        
        Args:
            start_date: Start of time period (inclusive)
            end_date: End of time period (exclusive)
            
        Returns:
            Dictionary mapping agent_type to total cost
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT agent_type, SUM(cost) as total_cost
                FROM cost_records
                WHERE timestamp >= ? AND timestamp < ?
                GROUP BY agent_type
                ORDER BY total_cost DESC
                """,
                (start_date, end_date)
            )
            rows = await cursor.fetchall()
            
            result = {row[0]: row[1] for row in rows}
        
        logger.debug(
            f"Cost by agent type from {start_date.date()} to {end_date.date()}: "
            f"{len(result)} agent types"
        )
        return result
    
    async def check_budget(self) -> BudgetStatus:
        """
        Check current budget utilization for today.
        
        Returns:
            BudgetStatus with current spend and utilization
            
        Raises:
            BudgetExceededError: If daily budget is exceeded
        """
        current_spend = await self.get_daily_cost()
        
        utilization_percent = (current_spend / self.daily_budget * 100) if self.daily_budget > 0 else 0
        is_over_budget = current_spend > self.daily_budget
        remaining_budget = max(0.0, self.daily_budget - current_spend)
        
        status = BudgetStatus(
            daily_budget=self.daily_budget,
            current_spend=current_spend,
            utilization_percent=utilization_percent,
            is_over_budget=is_over_budget,
            remaining_budget=remaining_budget
        )
        
        if is_over_budget:
            logger.warning(
                f"Budget exceeded: ${current_spend:.2f} / ${self.daily_budget:.2f} "
                f"({utilization_percent:.1f}%)"
            )
        elif utilization_percent >= 80:
            logger.warning(
                f"Budget threshold reached: ${current_spend:.2f} / ${self.daily_budget:.2f} "
                f"({utilization_percent:.1f}%)"
            )
        
        return status
    
    async def get_cost_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, any]:
        """
        Get comprehensive cost summary for a time period.
        
        Args:
            start_date: Start of time period (inclusive)
            end_date: End of time period (exclusive)
            
        Returns:
            Dictionary with total cost, cost by model, and cost by agent type
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Get total cost
            cursor = await db.execute(
                """
                SELECT COALESCE(SUM(cost), 0.0) as total_cost,
                       COUNT(*) as total_requests,
                       COALESCE(SUM(input_tokens), 0) as total_input_tokens,
                       COALESCE(SUM(output_tokens), 0) as total_output_tokens
                FROM cost_records
                WHERE timestamp >= ? AND timestamp < ?
                """,
                (start_date, end_date)
            )
            row = await cursor.fetchone()
            total_cost = row[0] if row else 0.0
            total_requests = row[1] if row else 0
            total_input_tokens = row[2] if row else 0
            total_output_tokens = row[3] if row else 0
        
        cost_by_model = await self.get_cost_by_model(start_date, end_date)
        cost_by_agent = await self.get_cost_by_agent_type(start_date, end_date)
        
        summary = {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "average_cost_per_request": total_cost / total_requests if total_requests > 0 else 0.0,
            "cost_by_model": cost_by_model,
            "cost_by_agent_type": cost_by_agent,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        logger.info(
            f"Cost summary from {start_date.date()} to {end_date.date()}: "
            f"${total_cost:.2f} across {total_requests} requests"
        )
        
        return summary
    
    async def get_hourly_costs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Tuple[datetime, float]]:
        """
        Get hourly cost breakdown for a time period.
        
        Args:
            start_date: Start of time period (inclusive)
            end_date: End of time period (exclusive)
            
        Returns:
            List of (hour_timestamp, cost) tuples
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT 
                    datetime(timestamp, 'start of hour') as hour,
                    SUM(cost) as hourly_cost
                FROM cost_records
                WHERE timestamp >= ? AND timestamp < ?
                GROUP BY hour
                ORDER BY hour
                """,
                (start_date, end_date)
            )
            rows = await cursor.fetchall()
            
            result = [(datetime.fromisoformat(row[0]), row[1]) for row in rows]
        
        logger.debug(
            f"Hourly costs from {start_date.date()} to {end_date.date()}: "
            f"{len(result)} hours"
        )
        return result
    
    async def get_top_expensive_tasks(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10
    ) -> List[Tuple[str, str, float]]:
        """
        Get the most expensive tasks by cost.
        
        Args:
            start_date: Start of time period (inclusive)
            end_date: End of time period (exclusive)
            limit: Maximum number of tasks to return
            
        Returns:
            List of (task_id, model_id, total_cost) tuples
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT task_id, model_id, SUM(cost) as total_cost
                FROM cost_records
                WHERE timestamp >= ? AND timestamp < ?
                GROUP BY task_id, model_id
                ORDER BY total_cost DESC
                LIMIT ?
                """,
                (start_date, end_date, limit)
            )
            rows = await cursor.fetchall()
            
            result = [(row[0], row[1], row[2]) for row in rows]
        
        logger.debug(
            f"Top {limit} expensive tasks from {start_date.date()} to {end_date.date()}"
        )
        return result
