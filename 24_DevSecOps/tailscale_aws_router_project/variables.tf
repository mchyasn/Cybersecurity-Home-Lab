# Declare the Tailscale auth key variable
variable "auth_key" {
  description = "The Tailscale auth key for setting up your Tailnet"
  type        = string
}

# Declare the subnet routes variable
variable "subnet_routes" {
  description = "Subnet routes to advertise"
  type        = list(string)
}

# Declare the SSH enablement flag
variable "enable_ssh" {
  description = "Enable SSH for Tailscale device"
  type        = bool
  default     = true
}

# Declare the SSH private key path variable
variable "ssh_private_key" {
  description = "Path to the private SSH key used to connect to EC2 instances"
  type        = string
}

# Declare the AWS profile variable (optional)
variable "aws_profile" {
  description = "The AWS CLI profile to use"
  type        = string
  default     = "default"
}

# Declare the AWS region variable
variable "aws_region" {
  description = "The AWS region where resources will be deployed"
  type        = string
  default     = "us-east-1"
}
