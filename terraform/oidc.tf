data "aws_eks_cluster" "shopsphere_oidc" {
  name = "shopsphere-phase9-eks"
}

resource "aws_iam_openid_connect_provider" "eks" {
  url = data.aws_eks_cluster.shopsphere_oidc.identity[0].oidc[0].issuer

  client_id_list = [
    "sts.amazonaws.com"
  ]

  tags = {
    Name = "shopsphere-phase9-eks-oidc"
  }
}
