#  This is the core infrastructure definition — where you declare all the resources you want Terraform to manage.

resource "aws_instance" "web_server" {
  ami           = "ami-08c40ec9ead489470"
  instance_type = var.instance_type

  tags = {
    Name = "MyWebServer"
  }
}
