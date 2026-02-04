# Pathway Design Principles

A minimalist, clean design system inspired by HEYTEA's aesthetic. This document outlines the core principles to maintain visual consistency across the application.

---

## 1. Color Palette

### Primary Colors
Use a **monochromatic palette** with minimal accent colors.

| Usage | Color | Tailwind Class |
|-------|-------|----------------|
| Primary text | Stone 900 | `text-stone-900` |
| Secondary text | Stone 500 | `text-stone-500` |
| Muted text | Stone 400 | `text-stone-400` |
| Borders | Stone 200 | `border-stone-200` |
| Subtle backgrounds | Stone 50 | `bg-stone-50` |
| Page background | Stone 50 | `bg-stone-50` |
| Cards/Modals | White | `bg-white` |

### Interactive Elements
| Usage | Color | Tailwind Class |
|-------|-------|----------------|
| Primary buttons | Stone 900 | `bg-stone-900 text-white` |
| Button hover | Stone 800 | `hover:bg-stone-800` |
| Selected states | Stone 900 + Stone 50 | `border-stone-900 bg-stone-50` |
| Focus rings | Stone 900 at 10% | `focus:ring-stone-900/10` |

### Status Colors (Use Sparingly)
| Status | Color | Usage |
|--------|-------|-------|
| Success/Active | Teal 50/700 | `bg-teal-50 text-teal-700` |
| Warning | Amber 50/700 | `bg-amber-50 text-amber-700` |
| Error | Red 50/700 | `bg-red-50 text-red-700` |

**Rules:**
- Never use more than **2 colors** on any single component
- Teal is reserved for **success states and positive actions only**
- Avoid blue, green, indigo, purple - stick to stone/teal

---

## 2. Typography

### Font Weights
- **Semibold (600)**: Page titles, card titles
- **Medium (500)**: Section headers, button text, emphasized content
- **Regular (400)**: Body text, descriptions

### Font Sizes
| Element | Size | Class |
|---------|------|-------|
| Page title | 2xl (24px) | `text-2xl font-semibold` |
| Card title | lg (18px) | `text-lg font-medium` |
| Section header | base (16px) | `text-base font-medium` |
| Body text | sm (14px) | `text-sm` |
| Helper text | xs (12px) | `text-xs text-stone-400` |

**Rules:**
- Avoid `font-bold` - use `font-semibold` maximum
- Keep line heights comfortable (1.5-1.7)
- Use `text-stone-900` for primary text, never `text-black`

---

## 3. Spacing & Layout

### Consistent Spacing Scale
```
4px  = p-1, gap-1
8px  = p-2, gap-2
12px = p-3, gap-3
16px = p-4, gap-4
24px = p-6, gap-6
32px = p-8, gap-8
```

### Cards & Containers
- Card padding: `p-4` to `p-6`
- Section gaps: `space-y-4` to `space-y-6`
- Modal max-width: `max-w-md` (small), `max-w-lg` (medium), `max-w-2xl` (large)

**Rules:**
- Use consistent padding within the same context
- Generous whitespace > cramped layouts
- Vertical rhythm should feel comfortable

---

## 4. Components

### Buttons
```tsx
// Primary - use for main actions
<Button>Save Changes</Button>
// → bg-stone-900 text-white

// Secondary - use for secondary actions
<Button variant="outline">Cancel</Button>
// → border-stone-200 text-stone-700

// Destructive - use sparingly for delete actions
<Button variant="destructive">Delete</Button>
// → bg-red-500 text-white
```

### Badges/Pills
```tsx
// Default - neutral information
<Badge>Label</Badge>
// → bg-stone-100 text-stone-700

// Success - active states, connected status
<Badge variant="success">Active</Badge>
// → bg-teal-50 text-teal-700

// Error - blocked states, errors
<Badge variant="error">Blocked</Badge>
// → bg-red-50 text-red-700
```

### Form Inputs
```tsx
// Standard input styling
className="px-3 py-2 border border-stone-200 rounded-lg text-sm
           focus:outline-none focus:ring-2 focus:ring-stone-900/10
           focus:border-stone-300"
```

### Loading Spinners
```tsx
// Small spinner
<div className="w-5 h-5 border-2 border-stone-200 border-t-stone-600
                rounded-full animate-spin" />

// Medium spinner
<div className="w-8 h-8 border-2 border-stone-200 border-t-stone-600
                rounded-full animate-spin" />
```

### Dropdowns & Select Menus

**IMPORTANT: Never use native browser `<select>` elements.** The default Apple/browser dropdowns look inconsistent and break the design aesthetic. Always use custom-styled dropdown components.

```tsx
// ❌ DON'T - Native select (looks like default Apple/browser dropdown)
<select className="...">
  <option value="a">Option A</option>
</select>

// ✅ DO - Custom dropdown component
<div className="relative">
  <button
    onClick={() => setIsOpen(!isOpen)}
    className="w-full flex items-center justify-between px-3 py-2
               border border-stone-200 rounded-lg text-sm text-left
               hover:border-stone-300 focus:outline-none
               focus:ring-2 focus:ring-stone-900/10"
  >
    <span className="text-stone-900">{selectedLabel}</span>
    <svg className="w-4 h-4 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  </button>

  {isOpen && (
    <div className="absolute z-10 mt-1 w-full bg-white border border-stone-200
                    rounded-lg shadow-lg py-1 max-h-60 overflow-auto">
      {options.map(option => (
        <button
          key={option.value}
          onClick={() => { setSelected(option.value); setIsOpen(false); }}
          className={`w-full px-3 py-2 text-left text-sm transition-colors
            ${selected === option.value
              ? 'bg-stone-50 text-stone-900 font-medium'
              : 'text-stone-700 hover:bg-stone-50'
            }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  )}
</div>
```

**Custom Dropdown Styling Requirements:**
- Trigger button: `border-stone-200`, `rounded-lg`, includes chevron icon
- Dropdown panel: `bg-white`, `border-stone-200`, `rounded-lg`, `shadow-lg`
- Options: `hover:bg-stone-50`, selected state with `bg-stone-50 font-medium`
- Use `z-10` or higher for dropdown positioning
- Include smooth transitions for open/close states

**For status/action dropdowns (like candidate status):**
```tsx
// Status dropdown with colored indicators
<button className="flex items-center gap-2 px-2 py-1 rounded text-sm ...">
  <span className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
  <span>{statusLabel}</span>
  <ChevronIcon />
</button>
```

---

## 5. Icons

### Guidelines
- Use **stroke icons** (outline style) for most cases
- Stroke width: `1.5` for subtle, `2` for emphasis
- Icon size: `w-4 h-4` (small), `w-5 h-5` (medium)
- Color: Match surrounding text color (`text-stone-500`, etc.)

### Example
```tsx
<svg className="w-4 h-4 text-stone-500" fill="none" stroke="currentColor"
     viewBox="0 0 24 24">
  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
</svg>
```

---

## 6. Borders & Shadows

### Borders
- Default border: `border-stone-200`
- Subtle border: `border-stone-100`
- Focus/Selected border: `border-stone-900` or `border-stone-300`

### Border Radius
- Small elements (inputs, badges): `rounded-lg`
- Cards: `rounded-lg`
- Avatars: `rounded-full`

### Shadows
- Avoid excessive shadows
- Use `shadow-sm` sparingly for elevated elements
- Cards should rely on borders, not shadows

---

## 7. Interactions

### Hover States
```css
/* Buttons */
hover:bg-stone-800  /* Primary */
hover:bg-stone-50   /* Outline/Ghost */

/* Links */
hover:text-stone-900

/* Cards/List items */
hover:bg-stone-50
```

### Transitions
- Always use transitions for interactive elements
- Standard: `transition-colors` for color changes
- Duration: 150-200ms
- Avoid excessive animations

```tsx
className="transition-colors hover:bg-stone-50"
```

### Selected States
```tsx
// Selected item in a list
className={selected
  ? 'border-stone-900 bg-stone-50'
  : 'border-stone-200 hover:border-stone-300'}
```

---

## 8. Patterns to Avoid

### Don't Do This
- Multiple bright colors on one screen
- Gradients (except subtle background gradients)
- Heavy shadows or 3D effects
- Indigo, blue, purple, green for primary UI elements
- Using `gray-*` classes (use `stone-*` instead)
- Bold font weights (`font-bold`)
- Large icons (> 24px) in UI elements
- Saturated colors for non-status elements
- **Native browser `<select>` elements** (looks like default Apple dropdown, breaks design consistency)

### Do This Instead
- Monochromatic stone palette with teal accents
- Flat design with subtle borders
- Soft, minimal shadows
- Consistent color usage across similar components
- `stone-*` for all neutral colors
- `font-medium` or `font-semibold` maximum
- Proportional icons that match text
- **Custom-styled dropdown components** with proper hover states and consistent styling

---

## 9. Quick Reference

### Color Cheat Sheet
```
Text:      stone-900, stone-700, stone-500, stone-400
Borders:   stone-200, stone-100, stone-300 (hover/focus)
Bg:        white, stone-50
Buttons:   stone-900 (primary), stone-100 (secondary)
Success:   teal-50/teal-700
Warning:   amber-50/amber-700
Error:     red-50/red-700
```

### Component Checklist
When building a new component, verify:
- [ ] Uses stone palette for neutrals (not gray)
- [ ] Uses teal only for success/positive states
- [ ] Has appropriate hover/focus states
- [ ] Uses consistent spacing
- [ ] Typography follows the scale
- [ ] Icons are proportional and use stroke style
- [ ] No more than 2 colors in the component
- [ ] Uses custom dropdowns (no native `<select>` elements)

---

## 10. Examples

### Good Example - Team Member Card
```tsx
<div className="flex items-center gap-3 p-4 border border-stone-200 rounded-lg">
  <div className="w-10 h-10 rounded-full bg-stone-100 text-stone-600
                  flex items-center justify-center font-medium">
    J
  </div>
  <div>
    <p className="font-medium text-stone-900">John Doe</p>
    <p className="text-sm text-stone-500">john@example.com</p>
  </div>
  <span className="ml-auto px-2 py-0.5 text-xs rounded-full
                   bg-teal-50 text-teal-700">
    Active
  </span>
</div>
```

### Bad Example - Too Many Colors
```tsx
// DON'T DO THIS
<div className="bg-blue-50 border-indigo-200">
  <div className="bg-purple-100 text-purple-600">J</div>
  <span className="bg-green-100 text-green-700">Active</span>
  <span className="bg-yellow-100 text-yellow-600">Admin</span>
</div>
```
