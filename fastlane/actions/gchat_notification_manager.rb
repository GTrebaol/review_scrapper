module Fastlane
  module Actions
    class GchatNotificationManagerAction < Action
      def self.run(params)
        is_delivery = params[:is_delivery]
        message = params[:message]
        webhook_url = params[:webhook_url]
        name = params[:name]
        build_env = params[:build_env]
        build_branch = params[:build_branch]
        version_name = params[:version_name]
        build_number = params[:build_number]
        extra_link = params[:extra_link]
        app_icon_url = params[:app_icon_url]
        os_icon_url = params[:os_icon_url]
        version = ""
        if extra_link.nil?
          extra_link = "Aucun lien fourni"
        end
        if build_number.nil?
          version = version_name
        else
          version = "#{version_name} (#{build_number})"
        end
        p params
        params = "-d '#{is_delivery}' -w '#{webhook_url}'"
        params += is_delivery == "false" ? " -m '#{message}'" : " -a '#{name}' -e '#{build_env}' -b '#{build_branch}' -v '#{version}' -r '#{extra_link}' -p '#{os_icon_url}'"
        params += "-i '#{app_icon_url}'" if(!app_icon_url.nil?)

        sh("python3 fastlane/#{ENV["FASTLANE_CACHE_IMPORT_PATH"]}/mobile.git/fastlane/scripts/gchat_notification_manager/notify.py #{params}")
      end

      def self.description
        "Send Google Chat notification"
      end

      def self.authors
        ["Mobile Indus"]
      end

      def self.details
        "Send Google Chat notification"
      end

      def self.available_options
        [
          FastlaneCore::ConfigItem.new(key: :is_delivery,
                                   env_name: "IS_DELIVERY",
                                description: "Boolean telling if the message if for an app delivery or not",
                                   optional: false,
                                       type: String),
          FastlaneCore::ConfigItem.new(key: :message,
                                  env_name: "MESSAGE",
                               description: "If no delivery, send simple message",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :webhook_url,
                                  env_name: "WEBHOOK_URL",
                               description: "The webhook URL where to publish the notification",
                                  optional: false,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :name,
                                  env_name: "APP_NAME",
                               description: "The application name",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :build_env,
                                  env_name: "APP_BUILD_ENV",
                               description: "The environment of the application",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :build_branch,
                                  env_name: "BUILD_BRANCH",
                               description: "The GIT branch from where the application is builded",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :version_name,
                                  env_name: "VERSION_NAME",
                               description: "The version of the application",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :build_number,
                                  env_name: "BUILD_NUMBER",
                               description: "The build number of the application",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :extra_link,
                                  env_name: "EXTRA_LINK",
                               description: "Extra link for the card",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :app_icon_url,
                                  env_name: "APP_ICON_URL",
                               description: "The URL of the icon of the application",
                                  optional: true,
                                      type: String),
          FastlaneCore::ConfigItem.new(key: :os_icon_url,
                                  env_name: "OS_ICON_URL",
                               description: "The URL of the icon of the OS",
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
