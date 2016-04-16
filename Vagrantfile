# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

INSTALL_DEPS=<<EOF
rm -rf .venv26 .venv27 .venv33 .venv34 .venv35
sudo add-apt-repository -y ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install -y python2.6-dev python2.7-dev python3.3-dev python3.4-dev python3.5-dev
sudo apt-get install -y python-virtualenv git ipython python3-pip silversearcher-ag
sudo pip3 install virtualenv
cd /vagrant
virtualenv -p /usr/bin/python2.6 .venv26
pip install -r requirements.txt
pip install -r test-requirements.txt
deactivate

virtualenv -p /usr/bin/python2.7 .venv27
source .venv27/bin/activate
easy_install -U pip
pip install -r requirements.txt
pip install -r test-requirements.txt
deactivate

virtualenv -p /usr/bin/python3.3 .venv33
source .venv33/bin/activate
pip3 install -r requirements.txt
pip3 install -r test-requirements.txt
deactivate

virtualenv -p /usr/bin/python3.4 .venv34
source .venv34/bin/activate
pip3 install -r requirements.txt
pip3 install -r test-requirements.txt
deactivate

virtualenv -p /usr/bin/python3.5 .venv35
source .venv35/bin/activate
pip3 install -r requirements.txt
pip3 install -r test-requirements.txt
deactivate

grep 'cd /vagrant' /home/vagrant/.bashrc || echo 'cd /vagrant' >> /home/vagrant/.bashrc
grep 'source .venv27/bin/activate' /home/vagrant/.bashrc || echo 'source .venv27/bin/activate' >> /home/vagrant/.bashrc
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
