variable "project_name" {
  type    = string
  default = "ttc-ridership"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "cluster_version" {
  type    = string
  default = "1.29"
}

variable "node_instance_type" {
  type    = string
  default = "t3.medium"
}
