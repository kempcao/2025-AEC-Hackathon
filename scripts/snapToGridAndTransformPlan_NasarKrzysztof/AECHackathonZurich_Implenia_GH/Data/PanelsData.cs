using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Newtonsoft.Json;

namespace AECHackathonZurich_Implenia_GH.Data
{
    public class PanelsData
    {
        [JsonProperty("attributes")]
        public Dictionary<string, string> Attributes { get; set; }
        [JsonProperty("items")]
        public Dictionary<string, Panel> Items { get; set; }
    }
}