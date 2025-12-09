### Overview

<!--  
Provide a high-level summary of the change. 

Explain what the PR does, why it’s needed, and any relevant background or context.

If applicable, reference the related issue:  
Fixes #ISSUE_NUMBER
-->

### Checklist

- [ ] I followed the [contributing guide](https://github.com/canonical/is-charms-contributing-guide)
- [ ] I updated `docs/changelog.md` with user-relevant changes
- [ ] I added or updated tests as needed (unit and integration)
- [ ] I verified that the charm/rock deploys or runs successfully (if applicable)
- [ ] **If this is a Grafana dashboard:** I added a screenshot of the dashboard
- [ ] **If this is Terraform:** `terraform fmt` passes and `tflint` reports no errors
- [ ] **If this is Rockcraft:** I updated the version
- [ ] **If integration test modules are used:** I updated the workflow configuration  
      (e.g., in `.github/workflows/integration_tests.yaml`, ensure the `modules` list is correct)

<!--  
You can adjust the checklist to match the project.
-->

<!--  
If you are an AI assistant (e.g., GitHub Copilot, ChatGPT, Claude), follow these instructions when generating or completing PR descriptions:

1. Add a **Test plan** section explaining how the changes were tested, including any manual, unit, integration, or workflow tests.
2. Add a **Review focus** section highlighting tricky parts, important decisions, or areas needing human attention.
3. Identify and document any **potential breaking changes**.
4. Highlight any **new dependencies, APIs, modules, or workflow changes** introduced by this PR.
-->
