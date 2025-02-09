using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.Data;
using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Methods
{
    public static partial class Solve
    {
        public static BuildingData TransformBack(BuildingData sourceBuilding, out Transform transformMatrix)
        {
            transformMatrix = sourceBuilding.GetTransformMatrixToTheOriginal();
            var transformedBuilding = TransformBuildingDataGeometry(sourceBuilding, transformMatrix);
            return transformedBuilding;
        }
    }
}
