# Research Paper Analysis System - Frontend

## Overview

A modern, responsive React-based web application for AI-powered research paper analysis. Built with **React 18**, **Vite**, **Tailwind CSS**, and **Framer Motion**, this frontend provides an intuitive interface for uploading PDFs, chatting with papers using RAG, generating summaries, taking quizzes, visualizing mind maps, and conducting autonomous research.

## Tech Stack

### Core Framework
- **React 18.3.1** - Modern React with hooks and concurrent features
- **Vite 5.3.3** - Lightning-fast build tool and dev server
- **JavaScript (JSX)** - Component-based architecture

### Styling & UI
- **Tailwind CSS 3.4.4** - Utility-first CSS framework
- **@tailwindcss/typography** - Beautiful typography for markdown content
- **Framer Motion 11.3.0** - Production-ready animation library
- **Lucide React 0.400.0** - Beautiful, consistent icon set

### Markdown & Math Rendering
- **react-markdown 9.0.1** - Render markdown in React
- **remark-gfm 4.0.0** - GitHub Flavored Markdown support
- **remark-math 6.0.0** - Math equation support
- **rehype-katex 7.0.0** - LaTeX math rendering
- **katex 0.16.10** - Fast math typesetting library

### HTTP Client
- **axios 1.7.2** - Promise-based HTTP client

## Architecture

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.jsx       # App header with branding
│   │   ├── ThemeToggle.jsx  # Dark/light mode toggle
│   │   ├── UploadArea.jsx   # PDF upload with drag & drop
│   │   ├── FeatureTabs.jsx  # Tab navigation
│   │   ├── ChatPanel.jsx    # RAG-based Q&A interface
│   │   ├── SummaryPanel.jsx # Comprehensive paper summary
│   │   ├── QuizPanel.jsx    # Interactive quiz
│   │   ├── MindmapPanel.jsx # Visual mind map
│   │   └── ResearchPanel.jsx # Autonomous research agent
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # Application entry point
│   └── index.css            # Global styles & Tailwind config
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
├── postcss.config.js        # PostCSS configuration
└── package.json             # Dependencies & scripts
```

## Features

### 1. PDF Upload & Processing
**Component**: `UploadArea.jsx`

- **Drag & Drop**: Intuitive file upload interface
- **File Validation**: PDF-only, max 5MB
- **Progress Tracking**: Real-time upload and processing status
- **Duplicate Detection**: Identifies previously uploaded papers
- **Async Processing**: Celery task integration for embedding generation
- **Status Polling**: Monitors background task completion

**User Flow**:
```
Upload PDF → OCR Processing → Embedding Generation → Ready for Analysis
```

**Features**:
- Visual progress indicators
- Error handling with user-friendly messages
- Duplicate paper detection with smart handling
- Automatic transition to analysis interface

### 2. AI Chat (RAG-based Q&A)
**Component**: `ChatPanel.jsx`

- **Conversational Interface**: Chat-style Q&A with the paper
- **RAG Integration**: Retrieval-Augmented Generation for accurate answers
- **Source Citations**: Expandable source documents with metadata
- **Markdown Support**: Rich text formatting with LaTeX math
- **Suggested Questions**: Quick-start prompts
- **Real-time Responses**: Streaming-ready architecture

**Features**:
- Message history with user/assistant distinction
- Collapsible source citations
- Syntax highlighting for code
- Math equation rendering (KaTeX)
- Auto-scroll to latest message
- Loading states with animations

**API Integration**:
```javascript
POST /api/chat/query
{
  paper_id: string,
  question: string,
  top_k: number (default: 15)
}
```

### 3. Comprehensive Summary
**Component**: `SummaryPanel.jsx`

- **9-Section Analysis**: Structured paper breakdown
  1. Executive Summary
  2. Background
  3. Research Problem
  4. Methodology
  5. Experiments
  6. Results & Findings
  7. Limitations
  8. Implications
  9. Future Work

- **Expandable Sections**: Click to expand/collapse
- **Color-Coded Icons**: Visual section identification
- **Markdown Rendering**: Full formatting support
- **Bulk Actions**: Expand/collapse all sections

**Features**:
- Smooth animations with Framer Motion
- Icon-based visual hierarchy
- Dark mode optimized
- LaTeX math support
- Table rendering
- Code syntax highlighting

### 4. Interactive Quiz
**Component**: `QuizPanel.jsx`

- **10 MCQ Questions**: AI-generated from paper content
- **Multiple Choice**: A, B, C, D options
- **Instant Feedback**: Correct/incorrect indicators
- **Explanations**: Detailed reasoning for correct answers
- **Score Tracking**: Real-time progress and final score
- **Retry Capability**: Reset and retake quiz

**Features**:
- Visual answer selection
- Progress bar
- Score calculation with percentage
- Color-coded feedback (green/red)
- Animated transitions
- Motivational messages based on score

**Quiz Flow**:
```
Generate Quiz → Answer Questions → Submit → View Results → Retry
```

### 5. Mind Map Visualization
**Component**: `MindmapPanel.jsx`

- **Interactive Visualization**: Markmap-based mind map
- **Hierarchical Structure**: Paper concepts in tree format
- **Zoom & Pan**: Interactive navigation
- **Expand/Collapse**: Node-level control
- **New Tab Support**: Open in separate window
- **Embedded Rendering**: iframe-based display

**Features**:
- Full-screen capable
- Responsive design
- Dark mode compatible
- LaTeX math in nodes
- Interactive controls guide

### 6. Deep Research Agent
**Component**: `ResearchPanel.jsx`

- **Autonomous Research**: LangGraph-powered agent
- **Web Search Integration**: Tavily + Perplexity APIs
- **Comprehensive Reports**: Markdown-formatted output
- **Multi-iteration**: Up to 15 research cycles
- **Source Citations**: Referenced findings
- **Download Reports**: Export as .md files

**Features**:
- Custom research queries
- Real-time progress indicators
- Markdown report rendering
- Download functionality
- Error handling
- New research capability

**Research Flow**:
```
Query → Planning → Search → Analysis → Evidence Collection → Report Generation
```

## Design System

### Color Palette

**Brand Colors**:
- Primary: Purple shades (#a855f7 to #3b0764)
- Brand: Blue shades (#0ea5e9 to #082f49)
- Accent: Orange shades (#f97316 to #7c2d12)
- Success: Green shades (#22c55e to #14532d)
- Neutral: Gray shades (#fafafa to #0a0a0a)

### Component Styles

**Cards**:
- `.glass-card` - Standard card with soft shadow
- `.card-elevated` - Elevated card with larger shadow

**Buttons**:
- `.btn-primary` - Primary action button (gradient)
- `.btn-secondary` - Secondary action button
- `.btn-ghost` - Minimal ghost button

**Badges**:
- `.badge-primary` - Primary badge
- `.badge-success` - Success badge
- `.badge-brand` - Brand badge
- `.badge-gradient` - Gradient badge

### Animations

**Keyframes**:
- `fadeIn` - Fade in animation
- `slideUp` - Slide up from bottom
- `slideDown` - Slide down from top
- `scaleIn` - Scale in animation
- `bounceSubtle` - Subtle bounce
- `shimmer` - Shimmer effect
- `gradient` - Gradient animation

**Usage**:
```css
animate-fade-in
animate-slide-up
animate-scale-in
animate-pulse-slow
animate-bounce-subtle
```

### Dark Mode

**Implementation**:
- Tailwind CSS dark mode with class strategy
- LocalStorage persistence
- System preference detection
- Smooth transitions
- Component-level dark variants

**Toggle**: `ThemeToggle.jsx` component with Sun/Moon icons

## API Integration

### Backend Proxy

**Vite Configuration** (`vite.config.js`):
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### API Endpoints

**Paper Management**:
- `POST /api/papers/upload-and-process` - Upload PDF
- `POST /api/papers/embed-store` - Generate embeddings
- `GET /api/papers/task-status/{task_id}` - Check task status
- `GET /api/papers/{paper_id}/status` - Paper status

**AI Analysis**:
- `GET /api/papers/{paper_id}/summary` - Generate summary
- `GET /api/papers/{paper_id}/quiz` - Generate quiz
- `GET /api/papers/{paper_id}/mindmap` - Generate mind map

**Chat**:
- `POST /api/chat/query` - RAG-based Q&A

**Research**:
- `POST /api/research/query` - Autonomous research

## State Management

### Component-Level State

**React Hooks Used**:
- `useState` - Local component state
- `useEffect` - Side effects and lifecycle
- `useRef` - DOM references and mutable values

**State Patterns**:
```javascript
// Loading states
const [isLoading, setIsLoading] = useState(false)

// Data states
const [data, setData] = useState(null)

// Error states
const [error, setError] = useState(null)

// UI states
const [isExpanded, setIsExpanded] = useState(false)
```

### App-Level State

**Main App State** (`App.jsx`):
```javascript
const [paperId, setPaperId] = useState(null)
const [activeTab, setActiveTab] = useState('chat')
const [uploadedFileName, setUploadedFileName] = useState('')
```

**State Flow**:
```
Upload Success → Set Paper ID → Enable Features → Tab Navigation
```

## Responsive Design

### Breakpoints

**Tailwind Breakpoints**:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px
- `2xl`: 1536px

### Mobile Optimization

**Features**:
- Responsive grid layouts
- Touch-friendly buttons
- Mobile-optimized spacing
- Collapsible sections
- Adaptive typography
- Hamburger menus (where applicable)

**Example**:
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

## Performance Optimizations

### Code Splitting
- Component-level lazy loading ready
- Dynamic imports for heavy components
- Route-based splitting (if routing added)

### Asset Optimization
- Vite's automatic code splitting
- Tree shaking for unused code
- CSS purging with Tailwind
- Image optimization ready

### Rendering Optimizations
- React.memo for expensive components
- useCallback for event handlers
- useMemo for computed values
- Key props for list rendering

## Accessibility

### ARIA Labels
```jsx
<button aria-label="Toggle theme">
  <Moon />
</button>
```

### Keyboard Navigation
- Tab navigation support
- Enter key for form submission
- Escape key for modals (if added)
- Focus indicators

### Semantic HTML
- Proper heading hierarchy
- Semantic elements (header, main, section)
- Alt text for images
- Form labels

### Color Contrast
- WCAG AA compliant colors
- Dark mode contrast optimization
- Focus visible states

## Development

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

Runs on `http://localhost:3000` with hot module replacement.

### Build for Production

```bash
npm run build
```

Outputs to `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure Details

### Component Breakdown

**Header.jsx**:
- App branding
- Online status indicator
- AWS Bedrock badge
- Theme toggle

**UploadArea.jsx**:
- Drag & drop zone
- File validation
- Upload progress
- Duplicate detection
- Error handling

**FeatureTabs.jsx**:
- Tab navigation
- Active state management
- Icon-based tabs
- Responsive grid

**ChatPanel.jsx**:
- Message list
- Input field
- Source citations
- Markdown rendering
- Auto-scroll

**SummaryPanel.jsx**:
- 9 expandable sections
- Icon-coded sections
- Bulk expand/collapse
- Markdown content

**QuizPanel.jsx**:
- Question cards
- Answer selection
- Score tracking
- Explanations
- Retry functionality

**MindmapPanel.jsx**:
- iframe embedding
- New tab support
- Loading states
- Error handling

**ResearchPanel.jsx**:
- Query input
- Progress indicators
- Report rendering
- Download functionality

### Styling Architecture

**Global Styles** (`index.css`):
- Tailwind directives
- Custom component classes
- Markdown styles
- Scrollbar customization
- Dark mode overrides

**Tailwind Config** (`tailwind.config.js`):
- Custom color palette
- Extended animations
- Custom shadows
- Typography plugin

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Environment Variables

No environment variables required. Backend URL is proxied through Vite.

## Deployment

### Build Output
```bash
npm run build
```

### Static Hosting
Deploy `dist/` folder to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages
- Any static hosting service

### Environment Configuration


Create Environment Files in the Frontend Directory

For Local Development (`.env.local` or `.env.development`)

```env
VITE_API_URL=http://localhost:8000
````

For Production (`.env.production`)

```env
VITE_API_URL=https://your-backend-api-url.com
````


## Future Enhancements

### Planned Features
- [ ] User authentication
- [ ] Paper library/history
- [ ] Collaborative annotations
- [ ] Export to PDF
- [ ] Multi-paper comparison
- [ ] Advanced search filters
- [ ] Bookmarking system
- [ ] Sharing capabilities

### Technical Improvements
- [ ] React Router for navigation
- [ ] Redux/Zustand for state management
- [ ] React Query for data fetching
- [ ] Storybook for component documentation
- [ ] Jest + React Testing Library
- [ ] E2E tests with Playwright
- [ ] PWA capabilities
- [ ] Offline support

