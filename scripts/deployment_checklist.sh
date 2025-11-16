#!/bin/bash

# =============================================================================
# ListingCraft Production Deployment Checklist Script
# =============================================================================
# This script helps verify that all deployment prerequisites are met
# Run before deploying to production
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ListingCraft Production Deployment Checklist            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check a requirement
check() {
    local test_name="$1"
    local command="$2"
    local is_critical="${3:-true}"

    printf "%-50s" "$test_name"

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        if [ "$is_critical" = "true" ]; then
            echo -e "${RED}✗ FAIL${NC}"
            ((FAILED++))
        else
            echo -e "${YELLOW}⚠ WARNING${NC}"
            ((WARNINGS++))
        fi
        return 1
    fi
}

# Function to check environment variable
check_env() {
    local var_name="$1"
    local is_critical="${2:-true}"

    check "Environment variable: $var_name" "[ ! -z \"\${$var_name}\" ]" "$is_critical"
}

echo -e "${BLUE}═══ 1. Environment Configuration ═══${NC}"
check ".env file exists" "[ -f .env ]"
check "DEBUG=False in .env" "grep -q '^DEBUG=False' .env"
check "DJANGO_SETTINGS_MODULE=prod" "grep -q 'DJANGO_SETTINGS_MODULE=config.settings.prod' .env"

echo ""
echo -e "${BLUE}═══ 2. Required Environment Variables ═══${NC}"
source .env 2>/dev/null || true
check_env "SECRET_KEY"
check_env "ALLOWED_HOSTS"
check_env "DB_NAME"
check_env "DB_USER"
check_env "DB_PASSWORD"
check_env "REDIS_URL"
check_env "DEEPSEEK_API_KEY"
check_env "STRIPE_LIVE_SECRET_KEY"
check_env "RESEND_API_KEY"

echo ""
echo -e "${BLUE}═══ 3. Security Settings ═══${NC}"
check "SECURE_SSL_REDIRECT=True" "grep -q '^SECURE_SSL_REDIRECT=True' .env"
check "SESSION_COOKIE_SECURE=True" "grep -q '^SESSION_COOKIE_SECURE=True' .env || [ \"\$SESSION_COOKIE_SECURE\" = \"True\" ]" "false"
check "CSRF_COOKIE_SECURE=True" "grep -q '^CSRF_COOKIE_SECURE=True' .env || [ \"\$CSRF_COOKIE_SECURE\" = \"True\" ]" "false"

echo ""
echo -e "${BLUE}═══ 4. Files & Dependencies ═══${NC}"
check "requirements/prod.txt exists" "[ -f requirements/prod.txt ]"
check "Dockerfile exists" "[ -f Dockerfile ]"
check "docker-compose.prod.yml exists" "[ -f docker-compose.prod.yml ]"
check "SECURITY.md exists" "[ -f SECURITY.md ]"
check "DEPLOYMENT.md exists" "[ -f DEPLOYMENT.md ]"

echo ""
echo -e "${BLUE}═══ 5. Database & Migrations ═══${NC}"
check "Migrations directory exists" "[ -d apps/subscriptions/migrations ]"
check "Initial migration exists" "ls apps/*/migrations/0001_*.py > /dev/null 2>&1"

echo ""
echo -e "${BLUE}═══ 6. Static Files ═══${NC}"
check "static directory exists" "[ -d static ]"
check "staticfiles directory (or can create)" "[ -d staticfiles ] || mkdir -p staticfiles"

echo ""
echo -e "${BLUE}═══ 7. Security Checks ═══${NC}"
if command -v python &> /dev/null; then
    check "Django security check" "python manage.py check --deploy --settings=config.settings.prod 2>&1 | grep -q 'System check identified no issues'" "false"
fi

echo ""
echo -e "${BLUE}═══ 8. Git Status ═══${NC}"
if command -v git &> /dev/null && [ -d .git ]; then
    check ".env not in git" "! git ls-files | grep -q '.env$'"
    check "No uncommitted critical files" "! git status --porcelain | grep -E '(settings|requirements)'" "false"
fi

echo ""
echo -e "${BLUE}═══ 9. Production Readiness ═══${NC}"
check "SECRET_KEY is not default" "! grep -q 'your-secret-key-here' .env"
check "Stripe live mode enabled" "grep -q '^STRIPE_LIVE_MODE=True' .env"
check "No debug code in settings" "! grep -E 'print\\(|pdb|breakpoint' config/settings/prod.py" "false"

echo ""
echo -e "${BLUE}═══ 10. Documentation ═══${NC}"
check "README.md up to date" "grep -q 'Phase 9' README.md" "false"
check "PLAN.md exists" "[ -f PLAN.md ]" "false"

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    SUMMARY                                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}Passed:   $PASSED${NC}"
echo -e "  ${RED}Failed:   $FAILED${NC}"
echo -e "  ${YELLOW}Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ All critical checks passed!                            ║${NC}"
    echo -e "${GREEN}║  Your application is ready for production deployment.     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

    if [ $WARNINGS -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}Note: There are $WARNINGS warnings. Review them before deploying.${NC}"
    fi

    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. docker-compose -f docker-compose.prod.yml up --build -d"
    echo "  2. docker-compose -f docker-compose.prod.yml exec web python manage.py migrate"
    echo "  3. docker-compose -f docker-compose.prod.yml exec web python manage.py init_plans"
    echo "  4. docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ $FAILED critical check(s) failed!                          ║${NC}"
    echo -e "${RED}║  Please fix the issues above before deploying.            ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
fi
