# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

INSTALL_DEPS=<<EOF
cd /vagrant
sudo add-apt-repository -y ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install -y python2.6-dev python2.7-dev python3.3-dev python3.4-dev python3.5-dev
sudo apt-get install -y python-virtualenv git ipython python3-pip silversearcher-ag
sudo pip3 install virtualenv

./run_tests.sh --remove-virtualenvs
./run_tests.sh --install-virtualenvs

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
