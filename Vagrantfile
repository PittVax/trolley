# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"

    config.vm.hostname = "trolley"
    
    config.vm.provider :virtualbox do |vb|
        vb.name = "trolley"
    end

    config.vm.network :forwarded_port, guest: 8000, host: 8000
    config.vm.network :private_network, ip: "192.168.123.45"

    # provision with simple shell script
    config.vm.provision "shell", path: "Vagrant.provision.sh"
end
