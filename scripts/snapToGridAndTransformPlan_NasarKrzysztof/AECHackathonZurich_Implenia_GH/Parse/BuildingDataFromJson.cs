using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.Data;

using Newtonsoft.Json;

namespace AECHackathonZurich_Implenia_GH.Parse
{
    public static class BuildingDataFromJson
    {
        public static BuildingData Parse(string jsonContent)
        {
            BuildingData buildingData = JsonConvert.DeserializeObject<BuildingData>(jsonContent);
            return buildingData;
        }
    }
}
