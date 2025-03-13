# Project structure

dynamic-workflow-ui/
├── app/                    # App Router
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx
│   ├── page.tsx            # Home page
│   └── chat/               # Chat interface
│       └── page.tsx
├── components/             # UI Components
│   ├── ui/                 # Basic UI components (using shadcn/ui)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── chat/
│   │   ├── chat-input.tsx
│   │   ├── message-list.tsx
│   │   └── message-item.tsx
│   └── workflow/
│       ├── workflow-diagram.tsx
│       ├── agent-card.tsx
│       └── workflow-steps.tsx
├── hooks/                  # Custom React hooks
│   ├── use-chat.ts
│   └── use-workflow.ts
├── lib/                    # Utility functions and API clients
│   ├── api.ts
│   └── utils.ts
├── types/                  # TypeScript type definitions
│   └── index.ts
├── public/                 # Static assets
│   └── images/
├── .env.local              # Environment variables
├── package.json
├── tsconfig.json
// └── README.md