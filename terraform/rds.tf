resource "aws_db_subnet_group" "shopsphere" {
  name = "shopsphere-phase9-db-subnet-group"

  subnet_ids = module.vpc.private_db_subnet_ids

  tags = {
    Name        = "shopsphere-phase9-db-subnet-group"
    Environment = "shared"
    Project     = "ShopSphere"
  }
}

resource "aws_security_group" "rds" {
  name        = "shopsphere-phase9-rds-sg"
  description = "PostgreSQL access from ShopSphere EKS nodes"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "shopsphere-phase9-rds-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_eks" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = "sg-099af10b8e577e78f"
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"

  description = "Allow PostgreSQL from EKS security group"
}

resource "aws_db_instance" "postgres" {
  identifier = "shopsphere-phase9-postgres"

  engine         = "postgres"
  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = "shopsphere"
  username = "shopsphere_admin"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.shopsphere.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 1
  deletion_protection     = true
  skip_final_snapshot     = false

  auto_minor_version_upgrade = true

  tags = {
    Name = "shopsphere-phase9-postgres"
  }
}
