output "cluster_name" {
  value = module.eks.cluster_name
}

output "kubeconfig_command" {
  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "backend_repo" {
  value = aws_ecr_repository.backend.repository_url
}

output "frontend_repo" {
  value = aws_ecr_repository.frontend.repository_url
}
