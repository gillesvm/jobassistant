resource "aws_vpc" "jobassistant_vpc" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, { Name = "${local.name_prefix}-vpc" })
}

resource "aws_internet_gateway" "jobassistant_igw" {
  vpc_id = aws_vpc.jobassistant_vpc.id
}

resource "aws_subnet" "public_jobassistant_a" {
  vpc_id            = aws_vpc.jobassistant_vpc.id
  cidr_block        = "10.1.1.0/24"
  availability_zone = "eu-central-1a"
}

resource "aws_subnet" "public_jobassistant_b" {
  vpc_id            = aws_vpc.jobassistant_vpc.id
  cidr_block        = "10.1.2.0/24"
  availability_zone = "eu-central-1b"
}

resource "aws_route_table" "public_jobassistant" {
  vpc_id = aws_vpc.jobassistant_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.jobassistant_igw.id
  }
}

resource "aws_route_table_association" "public_jobassistant_a" {
  subnet_id      = aws_subnet.public_jobassistant_a.id
  route_table_id = aws_route_table.public_jobassistant.id
}

resource "aws_route_table_association" "public_jobassistant_b" {
  subnet_id      = aws_subnet.public_jobassistant_b.id
  route_table_id = aws_route_table.public_jobassistant.id
}
