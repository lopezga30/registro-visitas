# Registro de Visitas

Proyecto end-to-end de aprendizaje cloud: sitio web con backend serverless desplegado en AWS.

## Arquitectura

```
[Usuario] → [CloudFront] → [S3 - Frontend]
                 ↕
         [API Gateway] → [Lambda (Python)] → [DynamoDB]
```

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML / CSS / JS |
| CDN | CloudFront + S3 |
| API | API Gateway + Lambda (Python 3.12) |
| Base de datos | DynamoDB (PAY_PER_REQUEST) |
| IaC | Terraform >= 1.5 |
| CI/CD | GitHub Actions + OIDC |

## Estructura

```
.
├── frontend/          # Sitio estático
├── backend/           # Lambda function
├── infra/             # Terraform
└── .github/workflows/ # Pipelines CI/CD
```

## Setup inicial (una sola vez)

### 1. Bucket S3 para el estado de Terraform

```bash
aws s3 mb s3://MI-NOMBRE-tfstate-bucket --region us-east-1
aws s3api put-bucket-versioning \
  --bucket MI-NOMBRE-tfstate-bucket \
  --versioning-configuration Status=Enabled
```

Reemplazá `REEMPLAZAR-tfstate-bucket` en `infra/main.tf` con el nombre que elegiste.

### 2. IAM Role para GitHub Actions (OIDC)

```bash
# Crear el Identity Provider de GitHub en tu cuenta AWS
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

Luego creá un IAM Role con este trust policy (reemplazá TU-USUARIO/TU-REPO):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::TU-ACCOUNT-ID:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:TU-USUARIO/TU-REPO:*"
      }
    }
  }]
}
```

Y adjuntale la política `AdministratorAccess` (o una política más restrictiva para producción real).

### 3. Secrets en GitHub

En tu repo → Settings → Secrets → Actions, agregá:

| Secret | Valor |
|--------|-------|
| `AWS_ROLE_ARN` | `arn:aws:iam::TU-ACCOUNT-ID:role/NOMBRE-DEL-ROLE` |

### 4. Environments en GitHub

En Settings → Environments, creá dos: `staging` y `production`.
Para `production`, activá "Required reviewers" para que pida aprobación manual.

## Flujo de trabajo

| Acción | Resultado |
|--------|-----------|
| Push a `staging` | Deploy automático en staging |
| Push a `main` | Deploy automático en production |
| PR abierto | Solo `terraform plan` (sin apply) |

## Desarrollo local

```bash
# Probar la Lambda localmente
cd backend
python -c "
import os; os.environ['TABLE_NAME']='test'
from lambda_function import handler
print(handler({'httpMethod':'GET','path':'/visits'}, None))
"
```
