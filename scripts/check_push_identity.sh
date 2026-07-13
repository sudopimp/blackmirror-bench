#!/usr/bin/env bash
# Fail if commits/push would attribute or auth as proeliteinterface instead of sudopimp.
set -euo pipefail
email=$(git config --get user.email)
login=$(gh api user --jq .login 2>/dev/null || true)
author=$(git var GIT_AUTHOR_IDENT)
if [[ "$email" == "proeliteinterface@gmail.com" ]]; then
  echo "FAIL: user.email is proeliteinterface@gmail.com" >&2
  exit 1
fi
if [[ "$email" != *sudopimp* ]]; then
  echo "FAIL: user.email should be sudopimp identity, got: $email" >&2
  exit 1
fi
if [[ -n "$login" && "$login" != "sudopimp" ]]; then
  echo "FAIL: gh active login is $login, need sudopimp" >&2
  exit 1
fi
if [[ "$author" == *proeliteinterface* ]]; then
  echo "FAIL: GIT_AUTHOR_IDENT contains proeliteinterface: $author" >&2
  exit 1
fi
echo "OK push identity: email=$email login=${login:-n/a} author=$author"
