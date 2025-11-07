| File             | Purpose                                              |
| ---------------- | ---------------------------------------------------- |
| **provider.tf**  | Configures your cloud provider (e.g., AWS)           |
| **main.tf**      | Declares the EC2 instance and runs your Docker setup |
| **variables.tf** | Lets you change region, instance type, etc. easily   |
| **outputs.tf**   | Prints your public IP or DNS name                    |

# Terraform Infrastructure

## Setup
1. Run `terraform init`
2. Run `terraform plan`
3. Run `terraform apply`
4. Run `terraform destory` to destory

## Variables
- `aws_region`: AWS region
- `instance_type`: EC2 instance type

## Outputs
- `public_ip`: The public IP of the deployed instance


## High Level Cycle 
provider.tf  →  main.tf  →  outputs.tf
       ↑            ↑
     variables.tf → |

🟩 provider.tf = who to talk to,
🟦 main.tf = what to build,
🟨 variables.tf = inputs,
🟥 outputs.tf = outputs (return values).