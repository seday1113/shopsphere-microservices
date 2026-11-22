terraform {
  backend "s3" {
    bucket       = "shopsphere-phase9-tfstate-450690783347"
    key          = "phase9/network/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
