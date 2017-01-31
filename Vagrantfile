# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04"

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
    config.cache.enable :apt
    config.cache.enable :npm
  end

  config.vm.define :geonotebook
  config.vm.hostname = "geonotebook"
  config.vm.network "forwarded_port", guest: 8888, host: 8888
  config.vm.post_up_message = "Geonotebook is running at http://localhost:8888"
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/opt/geonotebook"

  config.vm.provider "virtualbox" do |virtualbox|
    virtualbox.memory = ENV["VAGRANT_MEMORY"] || 2048
    virtualbox.customize ["modifyvm", :id, "--cpus", ENV["VAGRANT_CPUS"] || 2]
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "devops/site-dev.yml"
    ansible.galaxy_role_file = "devops/site-dev-requirements.yml"

    # TODO: This should be replaced with some general solution
    # which passes through GEONOTEBOOK_* env variables.
    ansible.extra_vars = {
      geonotebook_dir: ENV["GEONOTEBOOK_DIR"] || "/opt/geonotebook",
      geonotebook_version: ENV["GEONOTEBOOK_VERSION"] || "master",
      geonotebook_update: ENV["GEONOTEBOOK_UPDATE"] || false,
      geonotebook_force: ENV["GEONOTEBOOK_FORCE"] || false,
      geonotebook_auth_enabled: ENV["GEONOTEBOOK_AUTH_ENABLED"] || false,
      geonotebook_auth_token: ENV["GEONOTEBOOK_AUTH_TOKEN"] || ""
    }
  end
end
