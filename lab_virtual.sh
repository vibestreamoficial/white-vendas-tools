#!/bin/bash
# Monta um laboratorio virtual de seguranca (educativo/white hat).
# Escolha KVM (Linux) ou VirtualBox para rodar Kali Linux e VMs de treino.

echo "Escolha o hipervisor:"
echo "  1) KVM (Linux nativo - recomendado)"
echo "  2) VirtualBox"
read -r opcao

case "$opcao" in
  1)
    sudo apt update
    sudo apt install -y qemu-kvm libvirt-daemon-system virt-manager
    sudo adduser "$USER" libvirt 2>/dev/null || true
    echo "✅ KVM + Virtual Machine Manager instalados. Reinicie a sessao se pedir."
    ;;
  2)
    sudo apt update
    sudo apt install -y virtualbox virtualbox-ext-pack
    echo "✅ VirtualBox instalado."
    ;;
  *)
    echo "Opcao invalida."
    exit 1
    ;;
esac

cat <<'MSG'

LABORATORIO (tudo educativo - redes suas apenas):

1. Baixe o Kali Linux: https://www.kali.org/get-kali/ (VM image)
2. Baixe uma VM vulneravel para treino (ex.: Metasploitable 2)
3. Crie as VMs na mesma rede NAT no seu hipervisor
4. Estude: nmap, wireshark, metasploit (modo lab)

Nunca use essas tecnicas em redes de terceiros sem autorizacao.
MSG
