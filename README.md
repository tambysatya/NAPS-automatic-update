# NAPS Automatic Updater

## Protocol

This bot maintains the current and the expected configuration of the infrastructure.

Regularly, a thread checks they differ, and accordingly triggers an update:

- The VMs acknowledge to update and switch to "Pending"
- During the "Pending" phase, they update and arm a watchdog to rollback
- They notify if the update was successful
- If all the updates are successful, the bot sends a "Commit"
- If "Commit is received", the VMs disarm the watchdog

## Conflicts:

# The configuration of a VM differs from the "current" record maintained by the bot

This can occur if a VM rollbacks during the "Commit" phase, without having received its commit



TODO:
    NAPS should allow services to mention if they need to be updated manually (using a flag). Automatising the backups should help as well
