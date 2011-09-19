
require 'nanoc3/tasks'
require 'fileutils'

namespace :create do

  desc "Creates a new article"
  task :article do
    $KCODE = 'UTF8'
    require 'active_support/core_ext'
    require 'active_support/multibyte'
    @ymd = Time.now.to_s(:db).split(' ')[0]
    if !ENV['title']
      $stderr.puts "\t[error] Missing title argument.\n\tusage: rake create:article title='article title'"
      exit 1
    end

    title = ENV['title'].capitalize
    path, filename, full_path = calc_path(title)

    if File.exists?(full_path)
      $stderr.puts "\t[error] Exists #{full_path}"
      exit 1
    end

    template = <<TEMPLATE
---
created_at: #{@ymd}
excerpt: 
kind: article
publish: true
tags: [misc]
title: "#{title.titleize}"
---

TODO: Add content to `#{full_path}.`
TEMPLATE

    FileUtils.mkdir_p(path) if !File.exists?(path)
    File.open(full_path, 'w') { |f| f.write(template) }
    $stdout.puts "\t[ok] Edit #{full_path}"
  end

  def calc_path(title)
    year, month_day = @ymd.split('-', 2)
    path = "content/" + year + "/" 
    filename = month_day + "-" + title.parameterize('_') + ".md"
    [path, filename, path + filename]
  end
end

%w{yaml}.each{|lib| require lib}

config  = YAML.load(File.open("config.yaml"))

desc "Watches and automatically compiles the site"
task :auto => :build do
  sh "nanoc auto"
end

desc "Compiles all the static files"
task :compile_static do
  sh 'mkdir -p static/build'
  sh 'mkdir -p static/build/css'
  sh 'mkdir -p static/build/js'
  sh 'mkdir -p static/build/img'

  puts "Compliling LESS into CSS"
  sh 'lessc static/src/less/bootstrap.less --compress > static/build/css/stylesheet.css'

  #puts "Copying CSS files"
  #sh 'cp static/src/css/* static/build/css'
  
  puts 'Combining CSS files'
  sh 'cat static/src/css/* >> static/build/css/stylesheet.css'

  puts "Combining and minifying JS"
  sh "java -jar compiler.jar --js_output_file static/build/js/scripts.js --js static/src/js/prettify.js --js static/src/js/shadowbox.js"

  puts "Copying image files"
  sh 'cp -R static/src/img/* static/build/img'

  puts "Copying all static files"
  sh 'mkdir -p output/static'
  sh 'mv static/build output'
  sh 'rm -Rf output/static'
  sh 'mv output/build output/static'
end

desc "Compile the content"
task :compile do
  puts "Compiling content."
  sh "nanoc compile"
end

desc "Deploy to Server"
task :deploy => :build do
  puts "Deploying"
  sh "rsync -rsh='ssh' -avr -P output hasnain@mhlakhani.com:/home/hasnain/mhlakhani.com"
end

task :build => [:compile_static, :compile]

task :default => :auto
