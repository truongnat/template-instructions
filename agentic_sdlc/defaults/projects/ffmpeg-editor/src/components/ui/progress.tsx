import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const Progress = React.forwardRef<
    React.ElementRef<typeof ProgressPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => (
    <ProgressPrimitive.Root
        ref={ref}
        className={cn(
            "relative h-2 w-full overflow-hidden rounded-full bg-secondary",
            className
        )}
        {...props}
    >
        <ProgressPrimitive.Indicator asChild>
            <motion.div
                className="h-full w-full flex-1 bg-primary"
                initial={{ scaleX: 0, originX: 0 }}
                animate={{ scaleX: (value || 0) / 100 }}
                transition={{
                    type: "spring",
                    damping: 30,
                    stiffness: 200,
                }}
            />
        </ProgressPrimitive.Indicator>
    </ProgressPrimitive.Root>
));
Progress.displayName = ProgressPrimitive.Root.displayName;

export { Progress };
