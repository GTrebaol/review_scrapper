module Fastlane
  module Actions
    class DownloadBitriseArtifactsAction < Action
      def self.run(params)
          sh("python3 fastlane/#{ENV["FASTLANE_CACHE_IMPORT_PATH"]}/mobile.git/fastlane/scripts/download_bitrise_artifacts/download_bitrise_artifacts.py")
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
  
      def self.is_supported?(platform)
        true
      end
    end
  end
end
