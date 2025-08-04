#!/bin/bash

# Define the commands you want in each terminal
declare -a commands=(
  "claude > You are Agent 1 - The Architect. Create MULTI_AGENT_PLAN.md and initialize the project structure.",
  "claude > You are Agent 2. Read MULTI_AGENT_PLAN.md to get up to speed.",
  "claude > You are Agent 3. Read MULTI_AGENT_PLAN.md to get up to speed.",
  "claude > You are Agent 4. Read MULTI_AGENT_PLAN.md to get up to speed."
)

# Create .vscode directory if it doesn't exist
mkdir -p .vscode

# Begin tasks.json
cat <<EOF > .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
EOF

# Loop through commands and add each as a VS Code task
for i in "${!commands[@]}"; do
  task=$(cat <<EOT
    {
      "label": "Terminal $((i+1))",
      "type": "shell",
      "command": "${commands[$i]}",
      "problemMatcher": [],
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "dedicated"
      }
    }
EOT
)
  # Add comma unless it's the last element
  if [[ $i -lt $((${#commands[@]} - 1)) ]]; then
    echo "$task," >> .vscode/tasks.json
  else
    echo "$task" >> .vscode/tasks.json
  fi
done

# End tasks.json
echo "  ]" >> .vscode/tasks.json
echo "}" >> .vscode/tasks.json

echo "VS Code tasks generated. Run them via the Command Palette → Run Task."
