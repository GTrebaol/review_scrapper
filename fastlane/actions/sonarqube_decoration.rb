module Fastlane
    module Actions
      class SonarqubeDecorationAction < Action
        def self.run(params)
          project_name = params[:project_name]
          sh("python3 fastlane/#{ENV["FASTLANE_CACHE_IMPORT_PATH"]}/phenix-indus.git/fastlane/phenix-tools/scripts/sonarqube_decoration/sonarqube_decoration.py -a #{project_name}")
        end
  
        def self.description
          "Download artifacts between two bitrise builds"
        end
  
        def self.authors
          ["DO Mobile"]
        end
    
        def self.details
          "Download artifacts between two bitrise builds"
        end
  
        def self.available_options
          [
            FastlaneCore::ConfigItem.new(key: :project_name,
                                    env_name: "DO_MOBILE_TOOLS_SONARQUBE_PROJECT_NAME",
                                 description: "The sonarqube project name from which getting data",
                                    optional: false,
                                        type: String),
          ]
        end
  
        def self.is_supported?(platform)
          true
        end
      end
    end
  end
  