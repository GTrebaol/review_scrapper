module Fastlane
    module Actions
      class GitlabReleaseManagerAction < Action
        def self.run(params)
          project_id = params[:project_id]
          tag_name = params[:tag_name]
          app_name = params[:app_name]
          app_version = params[:app_version]
          description = params[:description]
          if description.nil? || description == ""
            extra_option = ""
          else
            description = description.gsub("'", " ")
            extra_option = "-d '#{description}'"
          end
          sh("python3 fastlane/#{ENV["FASTLANE_CACHE_IMPORT_PATH"]}/mobile.git/fastlane/scripts/gitlab_release_manager/gitlab_release_manager.py -p #{project_id} #{tag_name} \"#{app_name}\" #{app_version} #{extra_option}")
        end
  
        def self.description
          "GitLab Release Manager."
        end
  
        def self.authors
          ["DO Mobile"]
        end
    
        def self.details
          "Create or update a release based on a tag in a project"
        end
  
        def self.available_options
          [
            FastlaneCore::ConfigItem.new(key: :project_id,
                                    env_name: "DO_MOBILE_TOOLS_PROJECT_ID",
                                 description: "The GitLab project ID",
                                    optional: false,
                                        type: String),
            FastlaneCore::ConfigItem.new(key: :tag_name,
                                    env_name: "DO_MOBILE_TOOLS_TAG_NAME",
                                 description: "The tag name related to the release",
                                    optional: false,
                                        type: String),
            FastlaneCore::ConfigItem.new(key: :app_name,
                                    env_name: "DO_MOBILE_TOOLS_APP_NAME",
                                 description: "The app name delivered",
                                    optional: false,
                                        type: String),
            FastlaneCore::ConfigItem.new(key: :app_version,
                                    env_name: "DO_MOBILE_TOOLS_APP_VERSION",
                                 description: "The app version delivered",
                                    optional: false,
                                        type: String),
            FastlaneCore::ConfigItem.new(key: :description,
                                    env_name: "DO_MOBILE_TOOLS_DESCRIPTION",
                                 description: "Optional release description",
                                    optional: true,
                                        type: String)
          ]
        end
  
        def self.is_supported?(platform)
          true
        end
      end
    end
  end
  