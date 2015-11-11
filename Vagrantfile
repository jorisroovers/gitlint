# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

INSTALL_DEPS=<<EOF
sudo add-apt-repository -y ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install -y python-virtualenv git ipython python2.6 python2.6-dev python3-pip silversearcher-ag
sudo pip3 install virtualenv
cd /vagrant
virtualenv .venv
source .venv/bin/activate
easy_install -U pip
pip install -r requirements.txt
pip install -r test-requirements.txt
deactivate
virtualenv-3.4 .venv3
source .venv3/bin/activate
pip3 install -r requirements.txt
pip3 install -r test-requirements.txt
deactivate
virtualenv -p python2.6 .venv26/
pip install -r requirements.txt
pip install -r test-requirements.txt
deactivate
grep 'cd /vagrant' /home/vagrant/.bashrc ||
    echo 'cd /vagrant' >> /home/vagrant/.bashrc
grep 'source .venv/bin/activate' /home/vagrant/.bashrc ||
    echo 'source .venv/bin/activate' >> /home/vagrant/.bashrc
EOF

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.box = "ubuntu/trusty64"

    config.vm.define "dev" do |dev|
        dev.vm.provision "shell", inline: "#{INSTALL_DEPS}"
    end

    if Vagrant.has_plugin?("vagrant-cachier")
        config.cache.scope = :box
    end

end
