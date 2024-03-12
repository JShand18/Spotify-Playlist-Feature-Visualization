# # Creates and configures redshift cluster
# resource "aws_redshift_cluster" "redshift" {
#   cluster_identifier     = "sp-playlist-cluster-pipeline"
#   skip_final_snapshot    = true
#   master_username        = "awsuser"
#   master_password        = var.db_password
#   node_type              = "dc2.large"
#   cluster_type           = "single-node"
#   publicly_accessible    = "true"
#   iam_roles              = [aws_iam_role.redshift_role.arn]
#   vpc_security_group_ids = [aws_security_group.sg_redshift.id]

# }

# # Security group for redshift configures to allow all inbound/outbound traffic
# resource "aws_security_group" "sg_redshift" {
#   name = "sg_redshift"
#   ingress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

# }

# # S3 bucket read only access given to redshift cluster
# resource "aws_iam_role" "redshift_role" {
#   name                = "RedShiftLoadRole"
#   managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action = "sts:AssumeRole"
#         Effect = "Allow"
#         Sid    = ""
#         Principal = {
#           Service = "redshift.amazonaws.com"
#         }
#       },
#     ]
#   })
# }

