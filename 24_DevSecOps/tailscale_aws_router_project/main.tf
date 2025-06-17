
provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

#  VPC
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "main-vpc"
  }
}

#  public subnet
resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"  
  tags = {
    Name = "public-subnet"
  }
}

#  private subnet
resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"  

  tags = {
    Name = "private-subnet"
  }
}

#  an Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main_vpc.id

  tags = {
    Name = "main-gateway"
  }
}

#  a NAT Gateway
resource "aws_nat_gateway" "nat_gw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet.id

  tags = {
    Name = "main-nat-gateway"
  }
}

#  an Elastic IP for the NAT Gateway
resource "aws_eip" "nat_eip" {
  domain = "vpc"

  tags = {
    Name = "nat-eip"
  }
}

#  a route table for the public subnet
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

#  associate the route table with the public subnet
resource "aws_route_table_association" "public_route_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}

#  a route table for the private subnet
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gw.id
  }

  tags = {
    Name = "private-route-table"
  }
}

# associate the route table with the private subnet
resource "aws_route_table_association" "private_route_assoc" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_route_table.id
}

#  a security group for the public EC2 instance (Tailscale router)
resource "aws_security_group" "public_sg" {
  vpc_id = aws_vpc.main_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 41641
    to_port     = 41641
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "public-security-group"
  }
}

#  a security group for the private EC2 instance (Tailscale device)
resource "aws_security_group" "private_sg" {
  vpc_id = aws_vpc.main_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.public_subnet.cidr_block]
  }

  ingress {
    from_port   = 41641
    to_port     = 41641
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "private-security-group"
  }
}


#  the EC2 instance in the public subnet (Tailscale Router)
resource "aws_instance" "tailscale_router" {
  ami           = "ami-04a81a99f5ec58529"  
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.public_sg.id]

  associate_public_ip_address = true  
  key_name = "ts-key"

  tags = {
    Name = "tailscale-router"
  }

  provisioner "local-exec" {
    command = "echo 'Tailscale Router is ready'"
  }

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = file(var.ssh_private_key)
    host        = self.public_ip
  }
}

#  the EC2 instance in the private subnet (Tailscale Device)
resource "aws_instance" "tailscale_device" {
  ami           = "ami-04a81a99f5ec58529"  
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.private_subnet.id
  vpc_security_group_ids = [aws_security_group.private_sg.id]

  key_name = "ts-key"


  tags = {
    Name = "tailscale-device"
  }
}

output "tailscale_router_public_ip" {
  value = aws_instance.tailscale_router.public_ip
}

output "tailscale_device_private_ip" {
  value = aws_instance.tailscale_device.private_ip
}
