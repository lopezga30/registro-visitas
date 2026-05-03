# Proyecto: Registro de Visitas

Proyecto de aprendizaje cloud end-to-end en AWS. Sitio web donde los visitantes dejan su nombre y un mensaje. El objetivo es recorrer toda la cadena: código → Git → IaC → CI/CD → producción.

## Estado

**En producción y funcionando** (desde 2026-04-27)

- Sitio web: https://duwwxjtjmvv15.cloudfront.net
- API: https://4k4pvrtrp4.execute-api.us-east-1.amazonaws.com/production
- Repo GitHub: https://github.com/lopezga30/registro-visitas

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML / CSS (Space Grotesk) / JS vanilla |
| CDN | CloudFront + S3 |
| API | API Gateway + Lambda Python 3.12 |
| Base de datos | DynamoDB (PAY_PER_REQUEST) |
| IaC | Terraform >= 1.5, estado en S3 `lopezga30-tfstate` |
| CI/CD | GitHub Actions + OIDC (sin claves hardcodeadas) |

## Infraestructura AWS

- **Cuenta:** 931167744254 — usuario IAM: `lopezga30-user1`
- **Región:** us-east-1
- **S3 frontend:** `registro-visitas-frontend-production`
- **S3 tfstate:** `lopezga30-tfstate`
- **DynamoDB:** `registro-visitas-visits-production`
- **Lambda:** `registro-visitas-visits-production`
- **IAM Role CI/CD:** `registro-visitas-github-actions` (OIDC con GitHub)

## Estructura del proyecto

```
.
├── frontend/          # HTML/CSS/JS estático
│   ├── index.html     # Hero banner + layout 2 columnas
│   ├── style.css      # Diseño con colores vibrantes, fondo blanco
│   └── app.js         # Llama a la API, usa %%API_URL%% (se reemplaza en deploy)
├── backend/
│   └── lambda_function.py   # GET y POST /visits, boto3 + DynamoDB
├── infra/
│   ├── main.tf        # Todos los recursos AWS
│   ├── variables.tf   # aws_region, project_name, environment
│   └── outputs.tf     # cloudfront_url, cloudfront_distribution_id, api_url, s3_bucket
└── .github/workflows/
    ├── terraform.yml  # Se dispara con cambios en infra/ o backend/
    └── deploy.yml     # Se dispara con cambios en frontend/
```

## Cómo funciona el deploy

**Cambio de frontend:** editar `frontend/` → `git push` → pipeline `deploy.yml` sincroniza S3 e invalida CloudFront automáticamente.

**Cambio de backend:** editar `backend/lambda_function.py` → `git push` → pipeline `terraform.yml` reempaqueta el ZIP y actualiza Lambda.

**Cambio de infra:** editar `infra/*.tf` → `git push` → pipeline `terraform.yml` aplica los cambios en AWS.

## Comandos útiles

```bash
# Ver outputs de infraestructura (URLs, nombres de recursos)
cd infra && terraform output

# Ver pipelines recientes
gh run list --limit 5

# Ver logs de un pipeline
gh run view <run-id> --log

# Deploy manual del frontend
gh workflow run deploy.yml --field environment=production
```

## Features implementadas

- **Notificaciones por email (SES):** al recibir un mensaje, Lambda envía mail a lopezga30@hotmail.com usando lopezga30@gmail.com como remitente verificado. Hotmail como From fue rechazado silenciosamente por DMARC (p=reject de Microsoft).

## Próximos pasos sugeridos

1. Agregar ambiente `staging` completo (rama staging + recursos AWS separados)
2. Tests unitarios para Lambda ejecutados en el pipeline
3. Monitoreo con CloudWatch (métricas, logs, alertas)
4. Dominio personalizado con Route 53 + certificado SSL con ACM
5. Autenticación de usuarios con Amazon Cognito
6. Paginación en la API para soportar muchos mensajes
7. Aprobación manual en GitHub Environments antes de deploy a production

## Contexto del usuario

- Aprendiendo cloud AWS, proyecto para entender toda la cadena de desarrollo
- Prefiere aprender haciendo, con explicaciones de qué hace cada componente
- Herramientas instaladas: AWS CLI, Terraform, Git, GitHub CLI (`gh`)
- GitHub: `lopezga30`
