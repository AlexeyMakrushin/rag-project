# Frontend Guideline Document

This document outlines the architecture, design principles, and technologies for the web dashboard of your personal document indexing and AI-powered retrieval system. It’s written in everyday language so anyone—from a non-technical stakeholder to a new developer—can understand how the frontend is built and maintained.

## 1. Frontend Architecture

### 1.1 Overview
- **Framework**: React with Next.js
- **Styling**: CSS Modules
- **Data fetching**: Next.js built-in fetch (getServerSideProps / getStaticProps) and SWR

Next.js gives us server-side rendering (SSR) and static generation (SSG), which means pages load quickly and are indexed by search engines. React lets us break UI into small, reusable pieces called components.

### 1.2 Scalability, Maintainability, Performance
- **Scalability**: File-based routing in Next.js means adding new pages is as simple as dropping in new files. Component reuse lets us build features faster without duplicating code.
- **Maintainability**: CSS Modules scope styles by default, eliminating naming collisions. Clear folder structure (pages/, components/, styles/) keeps files organized.
- **Performance**: Next.js image optimization, automatic code splitting, and lazy loading of heavy components (via dynamic imports) reduce initial load times.

## 2. Design Principles

### 2.1 Usability
- Focus on simple, clear layouts: big search bar, clear buttons for syncing, indexing, and settings.
- Provide immediate feedback: loading spinners during API calls, toast notifications on success or error.

### 2.2 Accessibility
- Follow WCAG guidelines: semantic HTML (buttons, headings), proper aria-attributes on custom components, keyboard navigation support.
- Ensure color contrast meets accessibility standards (4.5:1 for normal text).

### 2.3 Responsiveness
- Mobile-first approach: design breakpoints at 320px, 768px, 1024px, 1440px. Grids and flex layouts adapt to screen sizes.
- Test on common devices: phones, tablets, and desktop screens.

## 3. Styling and Theming

### 3.1 Styling Approach
- **CSS Modules**: each component has its own `.module.css` file, keeping styles local and predictable.
- **Utility Classes**: small, reusable classes (e.g., `.mt-2`, `.px-4`) for spacing and layout tweaks.

### 3.2 Theming
- Use CSS variables in a top-level `:root` to define colors, font sizes, spacing units.
- Theme toggles (light/dark mode) by switching a single class on `<html>` and overriding CSS variables.

### 3.3 Visual Style
- Style: Modern flat design with subtle glassmorphism overlays on modals and cards.
- **Glassmorphism** on cards: `backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.6);`

### 3.4 Color Palette
| Name        | Hex        | Usage                          |
|-------------|------------|--------------------------------|
| Primary     | #0066FF    | Buttons, links                 |
| Secondary   | #00CC99    | Accent elements, highlights    |
| Background  | #F5F7FA    | Page background                |
| Surface     | #FFFFFF    | Cards, modals                  |
| Text Primary| #1A1A1A    | Main text                      |
| Text Secondary| #555555  | Subtext, captions              |
| Error       | #E54545    | Error messages, alerts         |
| Success     | #28A745    | Success notifications          |

### 3.5 Typography
- **Font Family**: Inter (system fallback: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto`)
- **Weights**: 400 (regular), 500 (medium), 700 (bold)
- **Base font size**: 16px; scale headings with rem units (e.g., `h1 { font-size: 2rem; }`).

## 4. Component Structure

### 4.1 Folder Organization
```
/src
  /components     # Reusable UI pieces (Buttons, Cards, Layouts)
  /features       # Feature-specific components (SearchBar, SyncStatus)
  /hooks          # Custom React hooks (useAuth, useSync)
  /pages          # Next.js pages (index.tsx, dashboard.tsx)
  /styles         # Global styles and CSS variables
  /utils          # Helper functions and constants
```

### 4.2 Reuse and Modularity
- Each component does one thing and is easily testable.
- Pass data via props and handle events via callbacks.
- Shared UI components (e.g., `<Button>`, `<Modal>`, `<Spinner>`) live in `components/ui/`.

### 4.3 Benefits
- Teams can work on different features without stepping on each other’s code.
- Bugs are easier to isolate and fix.
- Adding new features means assembling existing components rather than reinventing the wheel.

## 5. State Management

### 5.1 Data Fetching & Caching
- **SWR**: https://swr.vercel.app/ for fetching data from the FastAPI backend. It provides caching, revalidation, and built-in loading/error states.

### 5.2 Application State
- **React Context**: for global state such as user authentication status, theme (light/dark), and notification queue.
- Keep Context state minimal—only data needed across many components.

### 5.3 Local Component State
- Use `useState` and `useReducer` for form inputs, toggles, and other isolated UI states.

## 6. Routing and Navigation

### 6.1 Next.js Routing
- File-based routing: pages in `/pages` automatically become routes (e.g., `/pages/dashboard.tsx` → `/dashboard`).
- Dynamic routes for document detail pages: `/pages/documents/[id].tsx`.

### 6.2 Navigation Components
- `<Link>` from `next/link` for client-side transitions.
- Navbar component shows menu items (Search, Sync, Settings). Highlights active route.

### 6.3 Authentication Guards
- Wrap protected pages in a `withAuth` higher-order component that checks login status and redirects to `/login` if needed.

## 7. Performance Optimization

### 7.1 Code Splitting & Lazy Loading
- Use `dynamic(() => import('./HeavyComponent'))` for rarely used modules (e.g., analytics charts).

### 7.2 Image & Asset Optimization
- Next.js `<Image>` component for automatic resizing and lazy loading.
- Store icons as SVG and bundle via your component library.

### 7.3 Caching & CDN
- Leverage Next.js built-in ISR (Incremental Static Regeneration) for semi-static pages.
- Configure headers for long-term caching of static assets.

### 7.4 Bundle Analysis
- Use `next-bundle-analyzer` to identify large dependencies and trim where possible.

## 8. Testing and Quality Assurance

### 8.1 Unit Testing
- **Jest** + **React Testing Library**: test individual components and utility functions. Aim for coverage on critical modules (SearchBar, API calls).

### 8.2 Integration Testing
- Test how multiple components work together (e.g., form submission on the dashboard updating a list).

### 8.3 End-to-End Testing
- **Cypress**: simulate user flows (login, search, view document details, trigger re-index). Run in CI on every push.

### 8.4 Linting & Formatting
- **ESLint** with Next.js config
- **Prettier** for code formatting
- **Stylelint** for CSS Modules rules

### 8.5 CI/CD Integration
- Run tests, lint, and type checks (if using TypeScript) on GitHub Actions before merges.

## 9. Conclusion and Overall Frontend Summary

This frontend setup combines React and Next.js to deliver a fast, SEO-friendly dashboard that scales with your needs. We rely on component-based architecture, CSS Modules, and clear design principles (usability, accessibility, responsiveness) to ensure a maintainable codebase and a solid user experience. Theming and styling follow modern flat design with glassmorphism accents, backed by a consistent color palette and typography. State management uses SWR and React Context for predictable data flow, while Next.js handles routing and performance optimizations under the hood. Testing at all levels (unit, integration, end-to-end) ensures reliability, and CI/CD automates quality checks. Together, these guidelines form a clear, unambiguous blueprint for current development and future growth.