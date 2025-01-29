module Fastlane
    module Actions
      class GitlabTagsManagerAction < Action
        def self.run(params)
          project_id = params[:project_id]
          tag_name = params[:tag_name]
          sh("python3 fastlane/#{ENV["FASTLANE_CACHE_IMPORT_PATH"]}/mobile.git/fastlane/scripts/gitlab_tags_manager/gitlab_tags_manager.py -p #{tag_name} #{project_id}")
        end
  
        def self.description
          "GitLab Release Manager."
        end
  
        def self.authors
          ["DO Mobile"]
        end
    
        def self.details
          "Protect a tag in a project"
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
          ]
        end
  
        def self.is_supported?(platform)
          true
        end
      end
    end
  end
  