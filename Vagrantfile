# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

INSTALL_DEPS=<<EOF
cd /vagrant
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y --allow-unauthenticated python2.7-dev python3.5-dev python3.6-dev python3.7-dev python3.8-dev
sudo apt-get install -y --allow-unauthenticated python3.8-distutils # Needed to work around python3.8+virtualenv issue
sudo apt-get install -y python-virtualenv git ipython python-pip python3-pip silversearcher-ag jq
sudo apt-get purge -y python3-virtualenv
sudo pip3 install virtualenv

./run_tests.sh --uninstall --envs all
./run_tests.sh --install --envs all

grep 'cd /vagrant' /home/vagrant/.bashrc || echo 'cd /vagrant' >> /home/vagrant/.bashrc
grep 'source .venv27/bin/activate' /home/vagrant/.bashrc || echo 'source .venv27/bin/activate' >> /home/vagrant/.bashrc
EOF

INSTALL_JENKINS=<<EOF
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install -y openjdk-8-jre
sudo apt-get install -y jenkins
EOF

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.box = "ubuntu/xenial64"

    config.vm.define "dev" do |dev|
        dev.vm.provision "gitlint", type: "shell", inline: "#{INSTALL_DEPS}"
        # Use 'vagrant provision --provision-with jenkins' to only run jenkins install
        dev.vm.provision "jenkins", type: "shell", inline: "#{INSTALL_JENKINS}"
    end

    config.vm.network "forwarded_port", guest: 8080, host: 9080

    if Vagrant.has_plugin?("vagrant-cachier")
        config.cache.scope = :box
    end

end
