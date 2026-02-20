document.addEventListener('DOMContentLoaded', () => {
    // 1. Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.borderBottom = '1px solid rgba(255, 255, 255, 0.1)';
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.5)';
        } else {
            navbar.style.borderBottom = '1px solid transparent';
            navbar.style.boxShadow = 'none';
        }
    });

    // 2. Workflow Tabs functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const contentData = {
        review: {
            title: 'Deep Semantic Code Review',
            benefits: [
                '<span>✓</span> Detects security vulnerabilities & bugs',
                '<span>✓</span> Checks adherence to project architecture (via RAG)',
                '<span>✓</span> Suggests performance optimizations'
            ],
            command: '/asdlc-review',
            codeHeader: '<span class="title">ReviewerAgent</span>',
            codeContent: '<span class="comment">// Analyzing PR #42 against CONTEXT.md...</span>\n<span class="keyword">Found 1 critical issue:</span>\nThe authentication token validation does not follow \nthe project\'s standard JWT implementation pattern.\n\nSuggested fix generated. Apply? [y/N]'
        },
        test: {
            title: 'Automated Test Generation',
            benefits: [
                '<span>✓</span> Generates comprehensive unit & integration tests',
                '<span>✓</span> Automatically mocks external dependencies',
                '<span>✓</span> Follows framework-specific testing standards'
            ],
            command: '/asdlc-test',
            codeHeader: '<span class="title">TesterAgent</span>',
            codeContent: '<span class="comment">// Scanning auth.controller.ts context...</span>\n<span class="keyword">Generating passing test suite:</span>\n- Login success path (covers 4 assertions)\n- Invalid credentials (covers 2 assertions)\n- Rate limit exceeded (mocks Redis cache)\n\nTest suite saved to tests/auth.spec.ts'
        },
        refactor: {
            title: 'Context-Aware Refactoring',
            benefits: [
                '<span>✓</span> Safe extraction of logic into services',
                '<span>✓</span> Improves SOLID principle adherence',
                '<span>✓</span> Updates dependent tests automatically'
            ],
            command: '/asdlc-refactor',
            codeHeader: '<span class="title">DeveloperAgent</span>',
            codeContent: '<span class="comment">// Refactoring UserService class...</span>\n<span class="keyword">Action Plan:</span>\n1. Extract Email validation to EmailService\n2. Inject EmailService via constructor\n3. Update 14 dependent files\n\nRefactoring complete. 0 regressions detected.'
        },
        arch: {
            title: 'Architecture Brainstorming (ADR)',
            benefits: [
                '<span>✓</span> Proposes system designs based on requirements',
                '<span>✓</span> Analyzes trade-offs and consequences',
                '<span>✓</span> Generates standard markdown ADRs'
            ],
            command: '/asdlc-arch',
            codeHeader: '<span class="title">ArchitectAgent</span>',
            codeContent: '<span class="comment">// Brainstorming feature: Real-time notifications</span>\n<span class="keyword">Drafting ADR-005:</span>\nContext: We need to push alerts to 10k concurrent users.\nDecision: Implement Server-Sent Events (SSE) via existing Redis.\nTrade-offs: Lower overhead than WebSockets, but unidirectional.\n\nADR saved. Ready for review.'
        }
    };

    const workflowGrid = document.querySelector('.workflow-grid');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class
            tabBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked
            btn.classList.add('active');

            // Update content
            const tabId = btn.getAttribute('data-tab');
            const data = contentData[tabId];

            if (data && workflowGrid) {
                // Fade out
                workflowGrid.style.opacity = 0;
                
                setTimeout(() => {
                    const html = `
                        <div class="workflow-text">
                            <h3>${data.title}</h3>
                            <ul class="benefit-list">
                                ${data.benefits.map(b => `<li>${b}</li>`).join('')}
                            </ul>
                            <div class="command-box">${data.command}</div>
                        </div>
                        <div class="workflow-visual">
                            <div class="code-window">
                                <div class="code-header">
                                    <div class="dots"><span class="red"></span><span class="yellow"></span><span class="green"></span></div>
                                    ${data.codeHeader}
                                </div>
                                <pre><code>${data.codeContent}</code></pre>
                            </div>
                        </div>
                    `;
                    workflowGrid.innerHTML = html;
                    // Fade in
                    workflowGrid.style.opacity = 1;
                }, 200);
            }
        });
    });
});
