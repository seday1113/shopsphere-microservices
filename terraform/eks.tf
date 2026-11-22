module "eks" {
  source = "./modules/eks"

  cluster_name    = "shopsphere-phase9-eks"
  cluster_version = "1.34"

  cluster_role_arn = "arn:aws:iam::450690783347:role/ShopSphere-Phase9-EKS-Cluster-Role"
  node_role_arn    = "arn:aws:iam::450690783347:role/ShopSphere-Phase9-EKS-Node-Role"

  subnet_ids = module.vpc.private_app_subnet_ids

  node_instance_types = ["c7i-flex.large"]

  node_desired_size = 2
  node_min_size     = 1
  node_max_size     = 3
}
