# Creates S3 bucket
resource "aws_s3_bucket" "sp_playlist_bucket" {
  bucket        = var.s3_bucket
  force_destroy = true # deletes content upon terrform destroy
}

# Sets access control of bucker to private
resource "aws_s3_bucket_acl" "s3_sp_playlsit_bucket_acl" {
  bucket     = aws_s3_bucket.sp_playlist_bucket.id
  acl        = "private"
  depends_on = [aws_s3_bucket_ownership_controls.s3_bucket_acl_ownership]
}


resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership" {
  bucket = aws_s3_bucket.sp_playlist_bucket.id
  rule {
    object_ownership = "ObjectWriter"
  }
}
