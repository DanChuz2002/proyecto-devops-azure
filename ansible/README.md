# Automatización con Ansible

Este directorio contiene una configuración básica de Ansible para automatizar tareas de configuración y despliegue en la máquina virtual de Azure.

## Objetivo

Automatizar la instalación y configuración de componentes necesarios para la plataforma DevOps:

- Instalación de Docker
- Activación del servicio Docker
- Configuración de permisos del usuario
- Creación de carpetas de monitoreo
- Copia de archivos de despliegue
- Inicialización de Docker Swarm
- Despliegue del stack con Docker Swarm

## Archivos

- `inventory.ini`: define la máquina virtual de Azure.
- `playbook.yml`: contiene las tareas de automatización.
- `README.md`: documentación del uso de Ansible.

## Ejecución

Desde una terminal Linux o WSL:

```bash
ansible -i ansible/inventory.ini azure_vm -m ping