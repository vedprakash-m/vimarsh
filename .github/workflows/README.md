# GitHub Actions Configuration for Vimarsh

## Required Secrets

Configure these secrets in your GitHub repository settings:

### Backend Deployment
- `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` - Azure Functions publish profile
- `AZURE_CREDENTIALS` - Azure service principal credentials (JSON format)
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_RESOURCE_GROUP` - Azure resource group name

### Frontend Deployment
- `AZURE_STATIC_WEB_APPS_API_TOKEN` - Azure Static Web Apps deployment token
- `REACT_APP_API_BASE_URL` - Backend API base URL for frontend

## Workflow Files

1. **`.github/workflows/test.yml`** - Comprehensive test suite
   - Backend unit tests (pytest)
   - Frontend unit tests (Jest)
   - Integration tests
   - E2E tests
   - Performance tests
   - Security scanning
   - Code quality checks

2. **`.github/workflows/deploy.yml`** - Deployment pipeline
   - Runs tests before deployment
   - Deploys backend to Azure Functions
   - Deploys frontend to Azure Static Web Apps
   - Infrastructure deployment (production only)
   - Post-deployment validation
   - Deployment notifications

## Test Coverage

### Backend Tests
- Unit tests for all modules
- Integration tests for RAG pipeline
- Voice interface validation
- Analytics system validation
- Spiritual content quality tests
- PWA functionality tests
- Performance and load tests

### Frontend Tests
- Component unit tests
- TypeScript type checking
- Build verification
- PWA manifest validation

### Security & Quality
- Bandit security scanning
- Code formatting (Black)
- Import sorting (isort)
- Linting (flake8)

## Spiritual Context

All workflows include culturally appropriate messaging and emojis that honor the spiritual nature of the Vimarsh platform, maintaining reverence while providing technical feedback.

## Manual Deployment

You can trigger deployments manually through GitHub Actions with environment selection (staging/production).
