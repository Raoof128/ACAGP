# AWS Deployment Guide

Complete guide for deploying ACAGP to Amazon Web Services.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- AWS CLI v2.x (`aws --version`)
- kubectl 1.28+ (`kubectl version`)
- Terraform 1.6+ (`terraform version`)
- Docker 24+ (`docker version`)
- helm 3.x (`helm version`)

### AWS Account Setup
- AWS account with admin access
- AWS CLI configured: `aws configure`
- Region: `ap-southeast-2` (Sydney, Australia recommended for data sovereignty)

### Cost Estimate
Monthly cost for production deployment (~1000 organizations):

| Service | Configuration | Monthly Cost (AUD) |
|---------|--------------|-------------------|
| EKS Cluster | Control plane | $110 |
| EC2 Instances | 3x t3.xlarge | $450 |
| RDS PostgreSQL | db.r6g.xlarge | $550 |
| ElastiCache Redis | cache.r6g.large | $250 |
| S3 Storage | 500GB | $15 |
| Data Transfer | 1TB/month | $120 |
| CloudWatch | Logs + metrics | $50 |
| **Total** | | **~$1,545/month** |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        VPC (10.0.0.0/16)                     │
│                                                               │
│  ┌─────────────────────┐     ┌─────────────────────┐        │
│  │  Public Subnet 1    │     │  Public Subnet 2    │        │
│  │  10.0.1.0/24        │     │  10.0.2.0/24        │        │
│  │  ┌───────────────┐  │     │  ┌───────────────┐  │        │
│  │  │  NAT Gateway  │  │     │  │  NAT Gateway  │  │        │
│  │  └───────────────┘  │     │  └───────────────┘  │        │
│  │  ┌───────────────┐  │     │  ┌───────────────┐  │        │
│  │  │      ALB      │  │     │  │      ALB      │  │        │
│  │  └───────────────┘  │     │  └───────────────┘  │        │
│  └─────────────────────┘     └─────────────────────┘        │
│                                                               │
│  ┌─────────────────────┐     ┌─────────────────────┐        │
│  │ Private Subnet 1    │     │ Private Subnet 2    │        │
│  │ 10.0.11.0/24        │     │ 10.0.12.0/24        │        │
│  │  ┌───────────────┐  │     │  ┌───────────────┐  │        │
│  │  │  EKS Nodes    │  │     │  │  EKS Nodes    │  │        │
│  │  └───────────────┘  │     │  └───────────────┘  │        │
│  └─────────────────────┘     └─────────────────────┘        │
│                                                               │
│  ┌─────────────────────┐     ┌─────────────────────┐        │
│  │  Database Subnet 1  │     │  Database Subnet 2  │        │
│  │  10.0.21.0/24       │     │  10.0.22.0/24       │        │
│  │  ┌───────────────┐  │     │  ┌───────────────┐  │        │
│  │  │ RDS Primary   │  │     │  │ RDS Replica   │  │        │
│  │  └───────────────┘  │     │  └───────────────┘  │        │
│  │  ┌───────────────┐  │     │  ┌───────────────┐  │        │
│  │  │ ElastiCache   │  │     │  │ ElastiCache   │  │        │
│  │  └───────────────┘  │     │  └───────────────┘  │        │
│  └─────────────────────┘     └─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Step-by-Step Deployment

### 1. Prepare Infrastructure Code

```bash
cd infrastructure/terraform/aws

# Initialize Terraform
terraform init

# Review planned changes
terraform plan -var-file=production.tfvars

# Apply infrastructure
terraform apply -var-file=production.tfvars
```

### 2. Configure kubectl

```bash
# Get EKS cluster credentials
aws eks update-kubeconfig \
  --region ap-southeast-2 \
  --name acagp-production

# Verify connection
kubectl get nodes
```

### 3. Create Kubernetes Secrets

```bash
# Database credentials
kubectl create secret generic postgres-credentials \
  --from-literal=username=acagp_admin \
  --from-literal=password=YOUR_SECURE_PASSWORD \
  --from-literal=database=acagp

# Application secrets
kubectl create secret generic app-secrets \
  --from-literal=secret-key=YOUR_JWT_SECRET \
  --from-literal=sentry-dsn=YOUR_SENTRY_DSN

# AWS credentials (for S3 access)
kubectl create secret generic aws-credentials \
  --from-literal=access-key-id=YOUR_ACCESS_KEY \
  --from-literal=secret-access-key=YOUR_SECRET_KEY
```

### 4. Deploy Application

```bash
# Deploy backend
kubectl apply -f infrastructure/k8s/backend-deployment.yaml
kubectl apply -f infrastructure/k8s/backend-service.yaml

# Deploy Celery workers
kubectl apply -f infrastructure/k8s/celery-deployment.yaml

# Deploy frontend
kubectl apply -f infrastructure/k8s/frontend-deployment.yaml
kubectl apply -f infrastructure/k8s/frontend-service.yaml

# Deploy ingress
kubectl apply -f infrastructure/k8s/ingress.yaml
```

### 5. Run Database Migrations

```bash
# Get backend pod name
POD=$(kubectl get pods -l app=acagp-backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec $POD -- alembic upgrade head

# Seed initial data
kubectl exec $POD -- python -m scripts.seed_data
```

### 6. Configure DNS

```bash
# Get ALB DNS name
kubectl get ingress acagp-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Create Route 53 record
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch file://dns-record.json
```

Example `dns-record.json`:
```json
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "acagp.yourdomain.com",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{
        "Value": "your-alb-dns-name.ap-southeast-2.elb.amazonaws.com"
      }]
    }
  }]
}
```

### 7. Configure SSL Certificate

```bash
# Request ACM certificate
aws acm request-certificate \
  --domain-name acagp.yourdomain.com \
  --validation-method DNS \
  --region ap-southeast-2

# Validate certificate (follow AWS console instructions)

# Update ingress with certificate ARN
kubectl annotate ingress acagp-ingress \
  alb.ingress.kubernetes.io/certificate-arn=arn:aws:acm:...
```

## Post-Deployment Configuration

### Enable CloudWatch Logging

```bash
# Create log group
aws logs create-log-group --log-group-name /aws/eks/acagp-production

# Configure Fluent Bit
kubectl apply -f infrastructure/k8s/logging/fluent-bit-config.yaml
```

### Configure Autoscaling

```bash
# Install metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Configure HPA for backend
kubectl autoscale deployment acagp-backend \
  --cpu-percent=70 \
  --min=2 \
  --max=20

# Configure HPA for workers
kubectl autoscale deployment acagp-celery \
  --cpu-percent=80 \
  --min=5 \
  --max=50
```

### Set Up Backups

```bash
# Enable RDS automated backups
aws rds modify-db-instance \
  --db-instance-identifier acagp-production \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"

# Enable S3 versioning for evidence artifacts
aws s3api put-bucket-versioning \
  --bucket acagp-evidence-prod \
  --versioning-configuration Status=Enabled
```

## Monitoring & Logging

### CloudWatch Dashboards

Create custom dashboard:

```bash
aws cloudwatch put-dashboard \
  --dashboard-name ACAGP-Production \
  --dashboard-body file://cloudwatch-dashboard.json
```

### CloudWatch Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name acagp-high-error-rate \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name ErrorRate \
  --namespace ACAGP \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:ap-southeast-2:ACCOUNT:acagp-alerts

# Database CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name acagp-db-high-cpu \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=acagp-production \
  --alarm-actions arn:aws:sns:ap-southeast-2:ACCOUNT:acagp-alerts
```

### Application Monitoring

```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Install Grafana dashboards
kubectl apply -f infrastructure/k8s/monitoring/grafana-dashboards.yaml
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -l app=acagp-backend

# View pod logs
kubectl logs -f deployment/acagp-backend

# Describe pod for events
kubectl describe pod POD_NAME
```

### Database Connection Issues

```bash
# Test database connectivity from pod
kubectl exec -it POD_NAME -- psql -h RDS_ENDPOINT -U acagp_admin -d acagp

# Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Verify RDS is in correct subnet
aws rds describe-db-instances --db-instance-identifier acagp-production
```

### High Latency

```bash
# Check pod resource usage
kubectl top pods

# Check node resource usage
kubectl top nodes

# Scale up if needed
kubectl scale deployment acagp-backend --replicas=10
```

### SSL Certificate Issues

```bash
# Check certificate status
aws acm describe-certificate --certificate-arn arn:aws:acm:...

# View ALB listeners
aws elbv2 describe-listeners --load-balancer-arn arn:aws:elasticloadbalancing:...
```

## Rollback Procedure

```bash
# Rollback deployment
kubectl rollout undo deployment/acagp-backend

# Rollback database migration
kubectl exec POD_NAME -- alembic downgrade -1

# Restore RDS from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier acagp-production-restored \
  --db-snapshot-identifier acagp-production-snapshot-TIMESTAMP
```

## Cleanup

```bash
# Delete Kubernetes resources
kubectl delete -f infrastructure/k8s/

# Destroy Terraform infrastructure
cd infrastructure/terraform/aws
terraform destroy -var-file=production.tfvars
```

---

**Last Updated**: 2025-01-16
**Version**: 1.0.0
