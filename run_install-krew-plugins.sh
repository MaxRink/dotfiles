#!/bin/sh
if command -v kubectl krew >/dev/null 2>&1; then 
    kubectl krew install mtail
    kubectl krew install np-viewer
    kubectl krew install get-all
    kubectl krew install kubesec-scan
    kubectl krew install images

    kubectl krew install access-matrix
    kubectl krew install who-can
    kubectl krew install neat
    kubectl krew install sniff
    kubectl krew install trace
    kubectl krew install outdated
    kubectl krew install all
    kubectl krew install deprecations
    kubectl krew install debug-shell
    kubectl krew install fleet
    kubectl krew install grep
    kubectl krew install ingess-nginx
    kubectl krew install kyverno
    kubectl krew install net-forward
    kubectl krew install node-admin
    kubectl krew install node-restart
    kubectl krew install node-shell
    kubectl krew install podevents
    kubectl krew install socks5-proxy
    kubectl krew install whoami
    kubectl krew install view-cert
    kubectl krew install cluster-group
    kubectl krew install view-secret
    kubectl krew install resource-capacity
    kubectl krew install ctx
    kubectl krew install ns
    kubectl krew install modify-secret
    kubectl krew install oidc-login
    kubectl krew install topology 
    kubectl krew install skew
    #kubectl krew index add kvaps https://github.com/kvaps/krew-index
    #kubectl krew install kvaps/node-shell

else
    ./run_once_install-krew.sh
fi

if command -v kubectl df-pv > /dev/null 2>&1; then 
    echo "df-pv already installed"
else
    curl https://krew.sh/df-pv | bash
fi
