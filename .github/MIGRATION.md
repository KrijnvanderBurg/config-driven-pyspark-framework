# GitHub Actions Migration Guide

This document provides a comprehensive guide for migrating from the Azure DevOps pipeline setup to GitHub Actions.

## Overview

The GitHub Actions setup replicates and enhances the functionality of your Azure DevOps pipeline templates while following GitHub Actions best practices. The new system provides:

- **Better Performance**: Improved caching and parallel execution
- **Enhanced Security**: Native integration with GitHub security features
- **Simpler Management**: No external repositories or complex templating
- **Better Developer Experience**: More detailed feedback and artifact handling

## Architecture Comparison

### Azure DevOps Structure
```
.azuredevops/
├── v1/templates/
│   ├── atomic/python/          # Individual tool tasks
│   ├── composite/python/       # Tool combinations
│   └── solution/python/        # Complete workflows
├── pipelines/flint.yaml        # Project-specific pipeline
└── azure-pipelines.yaml       # Main pipeline entry point
```

### GitHub Actions Structure
```
.github/
├── workflows/                  # Complete workflows
│   ├── ci.yml                 # Main CI (replaces azure-pipelines.yaml)
│   ├── release.yml            # Release automation
│   ├── docs.yml               # Documentation
│   ├── security.yml           # Security scanning
│   ├── dependency-update.yml  # Automated updates
│   ├── auto-format.yml        # Code formatting
│   └── e2e-tests.yml          # End-to-end testing
└── actions/                   # Reusable actions
    ├── atomic/                # Individual tool actions
    └── composite/             # Tool combinations
```

## Key Improvements

### 1. Enhanced CI Pipeline
- **Matrix Testing**: Tests across Python 3.9-3.12
- **Better Caching**: Poetry dependencies cached per Python version
- **Parallel Execution**: Quality checks, tests, and security run in parallel
- **Artifact Management**: Comprehensive artifact upload and retention

### 2. Security Enhancements
- **CodeQL Integration**: Native GitHub security scanning
- **Scheduled Scans**: Daily security checks
- **Trusted Publishing**: Secure PyPI publishing without API keys
- **Comprehensive Coverage**: Both 1st and 3rd party vulnerability scanning

### 3. Automation Improvements
- **Auto-formatting**: Automatic code formatting on PRs
- **Dependency Updates**: Weekly automated dependency updates
- **Documentation**: Automatic GitHub Pages deployment
- **Release Management**: Streamlined release process

### 4. Developer Experience
- **Status Badges**: Real-time pipeline status
- **Detailed Feedback**: Better error reporting and artifact access
- **Manual Triggers**: Easy manual workflow execution
- **Environment-specific Deployments**: Proper environment management

## Migration Steps

### 1. Enable GitHub Actions
1. Ensure GitHub Actions are enabled in your repository settings
2. Set up branch protection rules for `main` branch
3. Configure required status checks

### 2. Configure Secrets and Variables
No secrets are required for basic functionality due to trusted publishing, but you may want to configure:

```bash
# Optional: CodeCov token for coverage reporting
CODECOV_TOKEN

# Optional: Custom PyPI token (if not using trusted publishing)
PYPI_API_TOKEN
```

### 3. Set Up Environments
Create environments in GitHub repository settings:
- **pypi**: For PyPI publishing (configure with PyPI trusted publishing)
- **github-pages**: For documentation deployment

### 4. Configure Branch Protection
Set up branch protection rules for `main`:
- Require status checks before merging
- Require up-to-date branches before merging
- Include administrators in restrictions

### 5. Enable GitHub Pages
1. Go to repository Settings > Pages
2. Set source to "GitHub Actions"
3. Documentation will be automatically deployed on main branch changes

## Workflow Triggers

### CI Pipeline (`ci.yml`)
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:  # Manual trigger
```

### Security Scanning (`security.yml`)
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:
  push:
    paths: ['pyproject.toml', 'poetry.lock']
```

### Dependency Updates (`dependency-update.yml`)
```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Mondays
  workflow_dispatch:
```

## Comparison with Azure DevOps Features

| Feature | Azure DevOps | GitHub Actions | Notes |
|---------|---------------|----------------|-------|
| **Parallel Jobs** | Manual configuration | Automatic | GitHub Actions handles parallelization better |
| **Caching** | Pipeline cache | Actions cache | More granular and efficient caching |
| **Artifacts** | Pipeline artifacts | Workflow artifacts | Better retention and access control |
| **Security Scanning** | Extensions required | Built-in | Native CodeQL and dependency scanning |
| **Secrets Management** | Variable groups | Repository secrets | More secure with environment-specific secrets |
| **Branch Policies** | Branch policies | Branch protection rules | Similar functionality with better UX |
| **Environments** | Environments | Environments | Feature parity with better integration |
| **Templates** | YAML templates | Reusable actions | More flexible and maintainable |
| **Monitoring** | Azure Monitor | GitHub Insights | Better native monitoring and insights |

## Performance Improvements

### Caching Strategy
```yaml
# More efficient dependency caching
- name: Cache Poetry dependencies
  uses: actions/cache@v3
  with:
    path: .venv
    key: poetry-${{ runner.os }}-${{ env.PYTHON_VERSION }}-${{ hashFiles('poetry.lock') }}
    restore-keys: |
      poetry-${{ runner.os }}-${{ env.PYTHON_VERSION }}-
```

### Matrix Builds
```yaml
# Test across multiple Python versions efficiently
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

### Conditional Execution
```yaml
# Skip unnecessary steps
- name: Run formatters
  if: github.event_name == 'pull_request'
```

## Troubleshooting

### Common Issues

1. **Action Not Found**
   ```
   Error: ./.github/actions/atomic/poetry-install/action.yml does not exist
   ```
   **Solution**: Ensure all action directories have an `action.yml` file

2. **Permission Denied**
   ```
   Error: Resource not accessible by integration
   ```
   **Solution**: Check workflow permissions and repository settings

3. **Cache Miss**
   ```
   Cache not found for input keys: poetry-ubuntu-latest-3.11-...
   ```
   **Solution**: This is normal for first runs; subsequent runs will use cache

### Debugging Workflows

1. **Enable Debug Logging**:
   - Set repository secret `ACTIONS_STEP_DEBUG` to `true`
   - Set repository secret `ACTIONS_RUNNER_DEBUG` to `true`

2. **Use Workflow Dispatch**:
   - Manually trigger workflows for testing
   - Add custom inputs for debugging

3. **Check Artifact Downloads**:
   - Download artifacts from failed runs
   - Review logs and test results

## Best Practices

### 1. Security
- Use `secrets.GITHUB_TOKEN` for repository access
- Configure environment-specific secrets
- Use trusted publishing for PyPI
- Regularly update action versions

### 2. Performance
- Use appropriate caching strategies
- Minimize artifact sizes
- Use conditional execution
- Leverage matrix builds efficiently

### 3. Maintenance
- Regularly update action versions
- Monitor workflow execution times
- Clean up old artifacts
- Review and update dependencies

### 4. Documentation
- Document custom workflows
- Maintain clear action descriptions
- Use meaningful job and step names
- Add status badges to README

## Next Steps

1. **Test the Migration**:
   - Create a test branch with the new workflows
   - Run through typical development scenarios
   - Verify all tools work as expected

2. **Update Documentation**:
   - Update README with new status badges
   - Document any project-specific workflows
   - Update contributor guidelines

3. **Clean Up**:
   - Archive or remove Azure DevOps pipelines
   - Update any references to old pipeline URLs
   - Remove unused configuration files

4. **Monitor and Optimize**:
   - Monitor workflow execution times
   - Optimize caching strategies
   - Fine-tune trigger conditions
   - Regular security and dependency updates

This migration provides a more robust, secure, and maintainable CI/CD pipeline while leveraging GitHub's native features for better developer experience.
