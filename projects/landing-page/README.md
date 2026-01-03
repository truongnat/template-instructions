# Agentic SDLC Landing Page

> Premium, accessible, and high-performance landing page built with Astro, React, and Tailwind CSS.

[![Deployment](https://img.shields.io/badge/deploy-vercel-black)](https://vercel.com)
[![Lighthouse](https://img.shields.io/badge/lighthouse-95%2B-success)](/)
[![Accessibility](https://img.shields.io/badge/a11y-WCAG%202.1%20AA-blue)](/)

---

## 🚀 Quick Start

```bash
# Install dependencies
bun install

# Start development server (http://localhost:4321)
bun dev

# Build for production
bun build

# Preview production build
bun preview
```

---

## 📦 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Astro** | 4.16+ | Static site generation, Islands architecture |
| **React** | 18.3+ | Interactive components (Terminal, FAQ) |
| **TypeScript** | 5.7+ | Type safety and better DX |
| **Tailwind CSS** | 3.4+ | Utility-first styling |
| **Lucide React** | Latest | Icon system |
| **Framer Motion** | 11.11+ | Advanced animations (optional) |

### Why This Stack?

- ⚡ **Performance**: Astro generates static HTML with minimal JavaScript
- 🎨 **Design Freedom**: Tailwind provides complete control over styling
- ♿ **Accessibility**: Built-in a11y features and best practices
- 🔍 **SEO**: Perfect for static, content-heavy landing pages
- 🚀 **Deploy Anywhere**: Vercel, Netlify, Cloudflare Pages, or any static host

---

## 🏗️ Project Structure

```
landing-page/
├── src/
│   ├── components/          # Astro & React components
│   │   ├── Hero.astro              # Hero section with terminal demo
│   │   ├── Features.astro          # Feature showcase
│   │   ├── BrainArchitecture.astro # AI brain visualization
│   │   ├── TerminalDemo.astro      # Interactive CLI demo
│   │   └── ... (13 total)
│   ├── layouts/
│   │   └── Layout.astro     # Base page layout with SEO
│   ├── pages/
│   │   └── index.astro      # Homepage (entry point)
│   └── styles/
│       └── global.css       # Design system & animations
├── public/                  # Static assets (images, fonts, etc.)
├── PROJECT-PLAN.md          # Comprehensive project plan
├── DESIGN-GUIDE.md          # Design system documentation
├── DEPLOYMENT.md            # Deployment instructions
├── DESIGN-IMPROVEMENTS.md   # UI/UX enhancement log
└── README.md                # This file
```

---

## 🎨 Design System

Our landing page follows a **premium, AI-inspired design language**:

- **Glassmorphism**: Modern, layered depth with backdrop blur
- **Gradient Animations**: Dynamic color shifts for visual interest
- **Neural Network Patterns**: Subtle AI-themed background elements
- **Fluid Typography**: Responsive type scale from mobile to desktop
- **Accessibility First**: WCAG 2.1 AA compliant, keyboard navigable

→ **Full design system**: See [`DESIGN-GUIDE.md`](./DESIGN-GUIDE.md)

---

## 🎯 Features

### Implemented ✅

- [x] **Hero Section**: Compelling value prop with animated terminal demo
- [x] **AI Agent Showcase**: 12 specialized agents with interactive cards
- [x] **Brain Architecture**: Animated knowledge graph visualization
- [x] **Role Explorer**: Interactive agent role selector
- [x] **Use Cases**: Real-world application examples
- [x] **Quick Start**: 3-step installation guide
- [x] **FAQ Section**: Accordion-style common questions
- [x] **Mobile Responsive**: Optimized for all screen sizes (320px - 1920px+)
- [x] **Accessibility**: Skip links, ARIA labels, keyboard navigation
- [x] **Performance**: Optimized animations, lazy loading

### In Progress 🟡

- [ ] SEO Optimization (meta tags, sitemap, structured data)
- [ ] Analytics Integration (Plausible/Fathom)
- [ ] Performance Benchmarking (Lighthouse CI)
- [ ] A/B Testing Setup

### Planned 🔮

- [ ] Blog/Documentation Integration
- [ ] Interactive Playground
- [ ] Video Tutorials
- [ ] Community Showcase

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Target Device |
|------------|-------|---------------|
| `mobile` | 0-639px | Smartphones |
| `sm` | 640px+ | Tablet portrait |
| `md` | 768px+ | Tablet landscape |
| `lg` | 1024px+ | Desktop |
| `xl` | 1280px+ | Large desktop |
| `2xl` | 1536px+ | Ultra-wide screens |

---

## ♿ Accessibility

We're committed to **WCAG 2.1 AA compliance**:

- ✅ Semantic HTML with proper heading hierarchy
- ✅ Skip-to-content link for keyboard users
- ✅ All interactive elements have visible focus states
- ✅ Color contrast ratios meet or exceed 4.5:1
- ✅ Respect `prefers-reduced-motion` for animations
- ✅ ARIA labels on all icons and interactive elements
- ✅ Touch targets ≥44×44px (iOS HIG compliance)

**Test with:**
```bash
# Automated accessibility testing
npm run test:a11y

# Manual testing: Use keyboard (Tab, Enter, Escape)
# Screen readers: NVDA (Windows), VoiceOver (macOS/iOS)
```

---

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect Repository**:
   - Import repo in Vercel dashboard
   - Framework: Astro
   - Build command: `bun build`
   - Output directory: `dist`

2. **Environment Variables**: None required for static site

3. **Deploy**: Automatic on every push to `main`

→ **Full deployment guide**: See [`DEPLOYMENT.md`](./DEPLOYMENT.md)

### Other Platforms

- **Netlify**: Drag-and-drop `dist/` folder or connect Git repo
- **Cloudflare Pages**: Direct Git integration
- **GitHub Pages**: Use GitHub Actions for deployment
- **AWS S3 + CloudFront**: Upload `dist/` to S3, configure CloudFront

---

## 📊 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| **Lighthouse Performance** | ≥95 | 🟡 Testing |
| **Lighthouse Accessibility** | 100 | ✅ Achieved |
| **Lighthouse SEO** | 100 | 🟡 In Progress |
| **First Contentful Paint** | <1.2s | 🟡 Testing |
| **Time to Interactive** | <2s | 🟡 Testing |
| **Total Bundle Size** | <100KB | ✅ Achieved |

---

## 🤝 Team & Roles

| Role | Responsibility | Status |
|------|----------------|--------|
| **@PM** | Project planning, timeline management | Active |
| **@UIUX** | Design system, component design | Active |
| **@DEV** | Implementation, performance optimization | Active |
| **@QA** | Testing, accessibility validation | Active |
| **@DEVOPS** | Deployment, monitoring, CI/CD | Pending |

---

## 📚 Documentation

| Document | Description | Link |
|----------|-------------|------|
| **PROJECT-PLAN.md** | Comprehensive project plan with timeline, metrics, architecture | [View](./PROJECT-PLAN.md) |
| **DESIGN-GUIDE.md** | Design system: colors, typography, components, animations | [View](./DESIGN-GUIDE.md) |
| **DEPLOYMENT.md** | Step-by-step deployment instructions for various platforms | [View](./DEPLOYMENT.md) |
| **DESIGN-IMPROVEMENTS.md** | UI/UX enhancement changelog | [View](./DESIGN-IMPROVEMENTS.md) |

---

## 🧠 Brain Integration

This project is integrated with the **Agentic SDLC Brain** system:

```bash
# Sync project documentation to Neo4j knowledge graph
python tools/neo4j/document_sync.py --type plans --path projects/landing-page

# Get AI-powered recommendations for landing page improvements
python tools/neo4j/learning_engine.py --recommend "landing page optimization"

# Record success patterns after major milestones
python tools/neo4j/learning_engine.py --record-success "landing-page-v1" \
  --task-type "web_development" \
  --success-approach "Astro + Tailwind + Glassmorphism"
```

---

## 🐛 Troubleshooting

### Dev server won't start
```bash
# Clear cache and reinstall
rm -rf node_modules .astro
bun install
bun dev
```

### Build fails
```bash
# Check TypeScript errors
bun run build --verbose

# Validate Tailwind config
npx tailwindcss --help
```

### Animations not working
- Check console for errors
- Ensure `prefers-reduced-motion` is not enabled (user or browser setting)
- Verify CSS animations are properly defined in `global.css`

---

## 📝 Development Workflow

1. **Create a feature branch**: `git checkout -b feature/new-section`
2. **Make changes**: Edit components or styles
3. **Test locally**: `bun dev` and verify at http://localhost:4321
4. **Commit with semantic message**: `git commit -m "feat: add testimonials section"`
5. **Push and create PR**: `git push origin feature/new-section`
6. **Review and merge**: Await team review

---

## 🎓 Learning Resources

- **Astro Docs**: https://docs.astro.build
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Accessibility**: https://www.w3.org/WAI/WCAG21/quickref/
- **Web Performance**: https://web.dev/performance

---

## 📄 License

MIT License - See root `LICENSE` file for details.

---

## 🙏 Acknowledgments

- **Design Inspiration**: Vercel, Linear, Stripe
- **Icon Set**: [Lucide Icons](https://lucide.dev)
- **Fonts**: Google Fonts (Inter, JetBrains Mono)
- **Framework**: Astro Team & Community

---

**Built with ❤️ by the Agentic SDLC Team**  
Last Updated: 2026-01-03  
Version: 1.2  

*Need help? Open an issue or check our [documentation](../../docs/).*
