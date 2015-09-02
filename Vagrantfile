# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

INSTALL_DEPS=<<EOF
sudo apt-get update
sudo apt-get install -y python-pip python-virtualenv git ipython
cd /vagrant
virtualenv .venv
source .venv/bin/active
pip install -r requirements.txt
pip install -r test-requirements.txt
EOF

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.box = "ubuntu/trusty64"

    config.vm.define "dev" do |dev|
        dev.vm.provision "shell", inline: " echo 'cd /vagrant' >> /home/vagrant/.bashrc && #{INSTALL_DEPS}"
    end

end
