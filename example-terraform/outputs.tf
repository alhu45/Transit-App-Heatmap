output "public_ip" {
  description = "Public IP address of the web server"
  value       = aws_instance.web_server.public_ip
}

output "website_url" {
  description = "Access URL"
  value       = "http://${aws_instance.web_server.public_ip}"
}

# Defines the values Terraform should print after deployment — e.g., IPs, URLs, ARNs.
