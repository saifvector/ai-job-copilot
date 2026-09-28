# Development Workflow & Standards

## Monorepo Tooling
* **Package Manager**: npm workspaces (`frontend`, `database`, `shared`)
* **Python Runtime**: Python 3.12 (via virtualenv `backend/venv`)
* **Docker**: Docker Compose for multi-container development

---

## Code Quality Standards

### Frontend Quality Checks
```bash
# Type check with strict TypeScript
npm run type-check --workspace=frontend

# Next.js and React ESLint
npm run lint --workspace=frontend

# Format code with Prettier
npm run format --workspace=frontend
```

### Backend Quality Checks
```bash
cd backend

# Lint code with Ruff
ruff check .

# Check formatting with Black
black --check .

# Static type analysis with Mypy
mypy .
```

### Automated Monorepo Lint Script
```bash
# Windows
scripts\lint.bat

# Linux / macOS
./scripts/lint.sh
```

---

## Branching & Commit Conventions

* **Branching Strategy**: Trunk-based with short-lived feature branches (`feat/`, `fix/`, `chore/`, `infra/`).
* **Conventional Commits**:
  - `feat(auth): initialize base security provider`
  - `fix(backend): correct correlation id propagation in async task`
  - `refactor(ui): extract reusable modal backdrop`
