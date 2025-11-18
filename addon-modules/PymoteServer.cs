using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Text;
using System.Text.Json;
using System.Threading;
using log4net;
using Nini.Config;
using OpenSim.Framework;
using OpenSim.Framework.Console;
using OpenSim.Region.Framework.Interfaces;
using OpenSim.Region.Framework.Scenes;
using Mono.Addins;

namespace OpenSim.Pymote
{
    /// <summary>
    /// Pymote - TCP-based Python remote control for OpenSimulator
    /// Allows Python scripts to execute OpenSim console commands via TCP
    /// </summary>
    [Extension(Path = "/OpenSim/RegionModules", NodeName = "RegionModule", Id = "PymoteServer")]
    public class PymoteServer : ISharedRegionModule
    {
        private static readonly ILog m_log = LogManager.GetLogger(MethodBase.GetCurrentMethod().DeclaringType);
        
        private bool m_Enabled = false;
        private int m_Port = 9500;
        private string m_BindAddress = "127.0.0.1";
        private int m_Timeout = 30;
        private int m_MaxConnections = 10;
        private Scene m_Scene;
        
        // TCP Server
        private TcpListener m_Listener;
        private Thread m_ListenerThread;
        private bool m_Running = false;
        
        // Configuration from Pymote.ini
        private Dictionary<string, bool> m_AllowedCommands = new Dictionary<string, bool>();
        private HashSet<string> m_AllowedIPs = new HashSet<string>();
        private Dictionary<string, int> m_CommandUserLevels = new Dictionary<string, int>();
        private bool m_RateLimitEnabled = false;
        private int m_MaxCommandsPerMinute = 60;
        private int m_MaxCommandsPerHour = 1000;
        private bool m_LogCommands = false;
        
        // Rate limiting tracking
        private Dictionary<string, List<DateTime>> m_CommandHistory = new Dictionary<string, List<DateTime>>();

        #region ISharedRegionModule

        public string Name
        {
            get { return "PymoteServer"; }
        }

        public Type ReplaceableInterface
        {
            get { return null; }
        }

        public void Initialise(IConfigSource config)
        {
            IConfig pymoteConfig = config.Configs["Pymote"];
            if (pymoteConfig != null)
            {
                m_Enabled = pymoteConfig.GetBoolean("Enabled", false);
                m_Port = pymoteConfig.GetInt("Port", 9500);
                m_BindAddress = pymoteConfig.GetString("BindAddress", "127.0.0.1");
                m_Timeout = pymoteConfig.GetInt("Timeout", 30);
                m_MaxConnections = pymoteConfig.GetInt("MaxConnections", 10);
                m_LogCommands = pymoteConfig.GetBoolean("LogCommands", false);
            }
            
            // Load command whitelist
            IConfig commandsConfig = config.Configs["PymoteCommands"];
            if (commandsConfig != null)
            {
                LoadCommandWhitelist(commandsConfig);
            }
            
            // Load IP whitelist
            IConfig ipConfig = config.Configs["PymoteIPWhitelist"];
            if (ipConfig != null)
            {
                LoadIPWhitelist(ipConfig);
            }
            
            // Load user level requirements
            IConfig levelsConfig = config.Configs["PymoteUserLevels"];
            if (levelsConfig != null)
            {
                LoadUserLevelRequirements(levelsConfig);
            }
            
            // Load rate limiting
            IConfig rateLimitConfig = config.Configs["PymoteRateLimit"];
            if (rateLimitConfig != null)
            {
                m_RateLimitEnabled = rateLimitConfig.GetBoolean("Enabled", false);
                m_MaxCommandsPerMinute = rateLimitConfig.GetInt("MaxCommandsPerMinute", 60);
                m_MaxCommandsPerHour = rateLimitConfig.GetInt("MaxCommandsPerHour", 1000);
            }

            if (m_Enabled)
            {
                m_log.InfoFormat("[PYMOTE]: Initializing Pymote TCP server on {0}:{1}", m_BindAddress, m_Port);
            }
        }

        public void AddRegion(Scene scene)
        {
            if (!m_Enabled)
                return;

            if (m_Scene == null)
                m_Scene = scene;
        }

        public void RemoveRegion(Scene scene)
        {
            if (!m_Enabled)
                return;
        }

        public void RegionLoaded(Scene scene)
        {
            if (!m_Enabled)
                return;
        }

        public void PostInitialise()
        {
            if (!m_Enabled)
                return;

            // Start TCP server
            StartTCPServer();
            
            m_log.InfoFormat("[PYMOTE]: TCP server ready on {0}:{1}", m_BindAddress, m_Port);
        }

        public void Close()
        {
            if (!m_Enabled)
                return;

            StopTCPServer();
        }

        #endregion

        #region TCP Server
        
        private void StartTCPServer()
        {
            try
            {
                IPAddress bindIP = IPAddress.Parse(m_BindAddress);
                m_Listener = new TcpListener(bindIP, m_Port);
                m_Listener.Start();
                m_Running = true;
                
                m_ListenerThread = new Thread(ListenForClients);
                m_ListenerThread.IsBackground = true;
                m_ListenerThread.Start();
                
                m_log.InfoFormat("[PYMOTE]: TCP server started on {0}:{1}", m_BindAddress, m_Port);
            }
            catch (Exception e)
            {
                m_log.ErrorFormat("[PYMOTE]: Failed to start TCP server: {0}", e.Message);
                m_Enabled = false;
            }
        }
        
        private void StopTCPServer()
        {
            m_Running = false;
            
            if (m_Listener != null)
            {
                try
                {
                    m_Listener.Stop();
                    m_log.Info("[PYMOTE]: TCP server stopped");
                }
                catch (Exception e)
                {
                    m_log.ErrorFormat("[PYMOTE]: Error stopping TCP server: {0}", e.Message);
                }
            }
            
            if (m_ListenerThread != null && m_ListenerThread.IsAlive)
            {
                m_ListenerThread.Join(1000);
            }
        }
        
        private void ListenForClients()
        {
            while (m_Running)
            {
                try
                {
                    if (m_Listener.Pending())
                    {
                        TcpClient client = m_Listener.AcceptTcpClient();
                        Thread clientThread = new Thread(() => HandleClient(client));
                        clientThread.IsBackground = true;
                        clientThread.Start();
                    }
                    else
                    {
                        Thread.Sleep(100);
                    }
                }
                catch (Exception e)
                {
                    if (m_Running)
                        m_log.ErrorFormat("[PYMOTE]: Error in listener: {0}", e.Message);
                }
            }
        }
        
        private void HandleClient(TcpClient client)
        {
            string clientIP = ((IPEndPoint)client.Client.RemoteEndPoint).Address.ToString();
            
            try
            {
                m_log.DebugFormat("[PYMOTE]: Client connected from {0}", clientIP);
                
                using (NetworkStream stream = client.GetStream())
                {
                    stream.ReadTimeout = m_Timeout * 1000;
                    stream.WriteTimeout = m_Timeout * 1000;
                    
                    byte[] buffer = new byte[4096];
                    int bytesRead = stream.Read(buffer, 0, buffer.Length);
                    
                    if (bytesRead > 0)
                    {
                        string request = Encoding.UTF8.GetString(buffer, 0, bytesRead).Trim();
                        string response = ProcessRequest(request, clientIP);
                        
                        byte[] responseBytes = Encoding.UTF8.GetBytes(response + "\n");
                        stream.Write(responseBytes, 0, responseBytes.Length);
                    }
                }
                
                m_log.DebugFormat("[PYMOTE]: Client disconnected from {0}", clientIP);
            }
            catch (Exception e)
            {
                m_log.WarnFormat("[PYMOTE]: Error handling client {0}: {1}", clientIP, e.Message);
            }
            finally
            {
                client.Close();
            }
        }
        
        private string ProcessRequest(string requestJson, string clientIP)
        {
            try
            {
                using (JsonDocument doc = JsonDocument.Parse(requestJson))
                {
                    JsonElement root = doc.RootElement;
                    
                    if (!root.TryGetProperty("Command", out JsonElement commandElement))
                    {
                        return CreateErrorResponse("Missing 'Command' field");
                    }
                    
                    string command = commandElement.GetString();
                    
                    if (m_LogCommands)
                        m_log.DebugFormat("[PYMOTE]: Executing command from {0}: {1}", clientIP, command);
                    
                    // Check if command is allowed
                    if (!IsCommandAllowed(command, clientIP))
                    {
                        return CreateErrorResponse($"Command not allowed: {command}");
                    }
                    
                    // Execute command
                    string output = ExecuteCommand(command);
                    
                    return CreateSuccessResponse(output);
                }
            }
            catch (JsonException e)
            {
                return CreateErrorResponse($"Invalid JSON: {e.Message}");
            }
            catch (Exception e)
            {
                m_log.ErrorFormat("[PYMOTE]: Error processing request: {0}", e.Message);
                return CreateErrorResponse($"Internal error: {e.Message}");
            }
        }
        
        private string ExecuteCommand(string command)
        {
            // Capture console output using a StringWriter
            StringBuilder output = new StringBuilder();
            StringWriter writer = new StringWriter(output);
            TextWriter oldOut = Console.Out;
            
            try
            {
                Console.SetOut(writer);
                MainConsole.Instance.RunCommand(command);
                writer.Flush();
            }
            finally
            {
                Console.SetOut(oldOut);
                writer.Dispose();
            }
            
            return output.ToString().TrimEnd();
        }
        
        private string CreateSuccessResponse(string result)
        {
            var response = new
            {
                Success = true,
                Result = result,
                Error = (string)null
            };
            
            return JsonSerializer.Serialize(response);
        }
        
        private string CreateErrorResponse(string error)
        {
            var response = new
            {
                Success = false,
                Result = (string)null,
                Error = error
            };
            
            return JsonSerializer.Serialize(response);
        }
        
        #endregion

        #region Configuration Loading
        
        private void LoadCommandWhitelist(IConfig config)
        {
            foreach (string key in config.GetKeys())
            {
                if (key.StartsWith("Allow_"))
                {
                    string commandName = key.Substring(6); // Remove "Allow_" prefix
                    bool allowed = config.GetBoolean(key, false);
                    m_AllowedCommands[commandName] = allowed;
                    
                    if (m_LogCommands)
                        m_log.DebugFormat("[PYMOTE]: Command '{0}' = {1}", commandName, allowed);
                }
            }
            
            m_log.InfoFormat("[PYMOTE]: Loaded {0} command permissions", m_AllowedCommands.Count);
        }
        
        private void LoadIPWhitelist(IConfig config)
        {
            foreach (string key in config.GetKeys())
            {
                if (key.StartsWith("AllowedIP"))
                {
                    string ip = config.GetString(key, "");
                    if (!string.IsNullOrEmpty(ip))
                    {
                        m_AllowedIPs.Add(ip);
                        m_log.DebugFormat("[PYMOTE]: Allowed IP: {0}", ip);
                    }
                }
            }
            
            if (m_AllowedIPs.Count > 0)
                m_log.InfoFormat("[PYMOTE]: IP whitelist enabled with {0} addresses", m_AllowedIPs.Count);
        }
        
        private void LoadUserLevelRequirements(IConfig config)
        {
            foreach (string key in config.GetKeys())
            {
                if (key.StartsWith("RequireLevel_"))
                {
                    string commandName = key.Substring(13); // Remove "RequireLevel_" prefix
                    int level = config.GetInt(key, 0);
                    m_CommandUserLevels[commandName] = level;
                    m_log.DebugFormat("[PYMOTE]: Command '{0}' requires level {1}", commandName, level);
                }
            }
            
            if (m_CommandUserLevels.Count > 0)
                m_log.InfoFormat("[PYMOTE]: User level requirements loaded for {0} commands", m_CommandUserLevels.Count);
        }
        
        #endregion
        
        #region Command Security
        
        /// <summary>
        /// Check if a command is allowed to execute
        /// </summary>
        public bool IsCommandAllowed(string command, string clientIP)
        {
            // Check IP whitelist if configured
            if (m_AllowedIPs.Count > 0 && !m_AllowedIPs.Contains(clientIP))
            {
                m_log.WarnFormat("[PYMOTE]: Command rejected from non-whitelisted IP: {0}", clientIP);
                return false;
            }
            
            // Check rate limiting
            if (m_RateLimitEnabled && !CheckRateLimit(clientIP))
            {
                m_log.WarnFormat("[PYMOTE]: Rate limit exceeded for IP: {0}", clientIP);
                return false;
            }
            
            // Extract command name (first word)
            string commandName = command.Split(' ')[0].ToLower();
            
            // Check exact match first
            if (m_AllowedCommands.ContainsKey(commandName))
            {
                bool allowed = m_AllowedCommands[commandName];
                
                if (m_LogCommands)
                    m_log.DebugFormat("[PYMOTE]: Command '{0}' allowed={1}", commandName, allowed);
                
                return allowed;
            }
            
            // Check wildcard patterns (e.g., show_* for show_regions, show_users)
            foreach (var kvp in m_AllowedCommands)
            {
                if (kvp.Key.EndsWith("*"))
                {
                    string pattern = kvp.Key.Substring(0, kvp.Key.Length - 1);
                    if (commandName.StartsWith(pattern))
                    {
                        if (m_LogCommands)
                            m_log.DebugFormat("[PYMOTE]: Command '{0}' matched wildcard '{1}' = {2}", commandName, kvp.Key, kvp.Value);
                        
                        return kvp.Value;
                    }
                }
            }
            
            // Default deny if not explicitly allowed
            if (m_LogCommands)
                m_log.WarnFormat("[PYMOTE]: Command '{0}' not in whitelist - denied", commandName);
            
            return false;
        }
        
        private bool CheckRateLimit(string clientIP)
        {
            DateTime now = DateTime.UtcNow;
            
            if (!m_CommandHistory.ContainsKey(clientIP))
            {
                m_CommandHistory[clientIP] = new List<DateTime>();
            }
            
            List<DateTime> history = m_CommandHistory[clientIP];
            
            // Remove old entries
            history.RemoveAll(dt => (now - dt).TotalHours > 1);
            
            // Check per-minute limit
            int lastMinute = history.Count(dt => (now - dt).TotalMinutes < 1);
            if (lastMinute >= m_MaxCommandsPerMinute)
            {
                m_log.WarnFormat("[PYMOTE]: Rate limit per-minute exceeded: {0}/{1}", lastMinute, m_MaxCommandsPerMinute);
                return false;
            }
            
            // Check per-hour limit
            if (history.Count >= m_MaxCommandsPerHour)
            {
                m_log.WarnFormat("[PYMOTE]: Rate limit per-hour exceeded: {0}/{1}", history.Count, m_MaxCommandsPerHour);
                return false;
            }
            
            // Add current command
            history.Add(now);
            
            return true;
        }
        
        #endregion
    }
}
