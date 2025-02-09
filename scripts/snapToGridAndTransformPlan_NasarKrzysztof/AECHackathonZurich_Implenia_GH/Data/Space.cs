using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Newtonsoft.Json;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Data
{
    public class Space
    {
        [JsonProperty("room_type")]
        public string RoomType { get; set; }

        [JsonProperty("apartment")]
        public string Apartment { get; set; }

        [JsonProperty("coordinates")]
        public List<Coordinate> Coordinates { get; set; }

        public Polyline ToPolyline()
        {
            Polyline polyline = new Polyline();
            foreach (Coordinate coord in Coordinates) {
                polyline.Add(new Point3d(coord.X, coord.Y, coord.Z));
            }
            return polyline;
        }

        public void SetCoordinates(Polyline polyline)
        {
            Coordinates = new List<Coordinate>();
            foreach (Point3d point in polyline) {
                Coordinates.Add(new Coordinate(point));
            }
        }
    }
}
