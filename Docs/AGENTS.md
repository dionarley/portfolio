# AGENTS.md - Portfolio Project Guidelines

## Project Overview

This is a personal portfolio website built with vanilla HTML, CSS, and JavaScript - no build tools, frameworks, or package managers. The site is fully static and runs directly in the browser.

## Project Structure

```
portfolio/
├── Docs/             # Documentação
│   ├── README.md     # Visão geral
│   ├── DEVELOPER.md # Guia devs
│   └── AGENTS.md    # Regras IA
├── index.html        # Main HTML page
├── styles.css        # All CSS styles
├── script.js         # JavaScript functionality
├── Dockerfile        # Docker image definition
├── nginx.conf        # Nginx configuration
├── docker-compose.yml # Docker Compose setup
└── LICENSE           # CC BY-SA 4.0 license
```

## Running the Project

Simply open `index.html` in any modern web browser. No build step or server required.

- **View locally**: Open the file directly in browser (file:// protocol)
- **Development**: Use a local server like `python -m http.server` or VS Code Live Server for hot reload

## Build/Lint/Test Commands

This project uses Docker with nginx for serving. No build system required.

### Docker Commands

```bash
# Build and run development server (hot reload via volumes)
docker-compose up --build

# Build and run production server
docker-compose up --build portfolio-prod

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Testing

- **Manual**: Open http://localhost:8080 in browser
- **Validate HTML**: Install html-validate (`npm i -g html-validate`) and run:
  ```bash
  html-validate index.html
  ```

### Single Test (HTML Validation)

```bash
# Validate HTML with html-validate
npx html-validate index.html
```

## Code Style Guidelines

### General Principles

- Keep code simple and readable - this is a vanilla JS project
- Avoid dependencies unless absolutely necessary
- Use semantic HTML5 elements
- Write responsive, mobile-first CSS
- Minimize code duplication across files
- Keep the site lightweight and fast-loading

### HTML

- Use semantic elements (`<header>`, `<nav>`, `<section>`, `<footer>`, `<main>`, `<article>`)
- Include proper meta tags for accessibility and SEO
- Use meaningful class and id names (kebab-case)
- Keep attributes properly quoted
- Validate HTML for accessibility (use semantic tags, alt text, ARIA where needed)
- Order attributes alphabetically within tags
- Use self-closing tags for void elements (`<img />`, `<br />`, etc.)
- Keep the DOM tree shallow - avoid unnecessary nesting

### CSS

- **Organization**: Use CSS custom properties (variables) at the top for colors, spacing, and constants
- **Naming**: kebab-case for classes/ids (`.skill-card`, `#contactForm`)
- **Formatting**: 
  - 4-space indentation (no tabs)
  - One property per line within rules
  - Alphabetical order within rules when practical
  - Use shorthand properties where appropriate
- **Selectors**: Prefer class selectors over IDs; avoid deep nesting (>3 levels)
- **Specificity**: Keep specificity low; avoid `!important` unless absolutely necessary
- **Responsiveness**: Use media queries for breakpoints; prefer relative units (rem, %, vw)
- **Animations**: Use CSS transitions and keyframes; keep animations smooth (60fps); use `transform` and `opacity` for best performance
- **Layout**: Use Flexbox for 1D layouts, Grid for 2D layouts
- **Mobile-first**: Write base styles for mobile, then add overrides for larger screens with `@media (min-width: ...)`

### JavaScript

- **Naming**: camelCase for variables/functions, PascalCase for constructors
- **Formatting**: 
  - 4-space indentation (no tabs)
  - Semicolons required at end of statements
  - Use const/let, avoid var
  - Prefer template literals over string concatenation
  - Use trailing commas in objects and arrays
- **Functions**: Keep functions small and focused; use arrow functions for callbacks
- **DOM**: Cache DOM references when used repeatedly; use event delegation where appropriate
- **Error handling**: Always check if elements exist before accessing (e.g., `if (element) {...}`)
- **Code placement**: Place scripts at end of body or use `defer` attribute
- **Events**: Use addEventListener instead of inline event handlers
- **Variables**: Declare variables where needed; avoid global scope pollution
- **Performance**: Minimize reflows; batch DOM updates; use requestAnimationFrame for animations

### General Conventions

- **Line length**: Keep lines under 120 characters when practical
- **Comments**: Use sparingly - code should be self-explanatory; use JSDoc for complex functions
- **Colors**: Use CSS variables for theming (see `:root` in styles.css)
- **Accessibility**: Ensure proper contrast ratios (4.5:1 for text), keyboard navigation, and screen reader support
- **Browser support**: Target modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions)

## Common Tasks

### Adding a new section
1. Add HTML markup in `index.html`
2. Add corresponding styles in `styles.css`
3. Add any JavaScript interactions in `script.js`

### Modifying the color scheme
Edit CSS variables in `:root` at the top of `styles.css`:
```css
:root {
    --primary-color: #3d4d1e;
    --secondary-color: #6b7a18;
    --accent-color: #e0b418;
    /* ... */
}
```

### Adding a new skill or project
Copy the existing card structure in `index.html` and modify the content.

### Modifying navigation
- Add new links in the `<nav>` element in `index.html`
- Update nav styles in `.nav-links` section of `styles.css`
- Ensure mobile menu handles new items correctly

### Working with animations
- Use CSS transitions for simple state changes (hover, focus)
- Use keyframes for complex multi-step animations
- Test animations on mobile devices for performance

## Performance Guidelines

- Minimize external dependencies (Font Awesome CDN is acceptable)
- Optimize images before adding (use WebP format when possible)
- Lazy load below-the-fold content if needed
- Keep total page weight under 500KB
- Defer non-critical JavaScript

## Accessibility Checklist

- [ ] All images have descriptive alt text
- [ ] Color contrast meets WCAG AA standards (4.5:1 for normal text)
- [ ] All interactive elements are keyboard accessible
- [ ] Form inputs have associated labels
- [ ] Heading hierarchy is logical (h1 -> h2 -> h3)
- [ ] Focus states are visible
- [ ] ARIA attributes used appropriately

## Important Notes

- This is a static site - no backend or API integration
- The contact form is client-side only: it validates the fields and opens the visitor's e-mail client via `mailto:` (no backend)
- Font Awesome is loaded via CDN for icons
- No browser-specific prefixes needed (modern browsers support all used CSS features)
- Site is fully responsive - test on mobile, tablet, and desktop

## License

Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0) - see LICENSE file